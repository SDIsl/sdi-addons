# Desarrollado por Juan Ormaechea (Mr. Rubik) — Todos los derechos reservados
# Este módulo está protegido por la Odoo Proprietary License v1.0
# Cualquier redistribución está prohibida sin autorización expresa.

import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from odoo import _, models, fields, api
from odoo.exceptions import UserError
import hashlib
import logging
import base64
import qrcode
from io import BytesIO

from cryptography.hazmat.backends import default_backend
import lxml.etree as LET
from signxml import XMLSigner, methods
from datetime import datetime, timedelta, timezone
import re
import platform
import socket
from ..verifactu.services.xml_builder.xml_builder import VerifactuXMLBuilder
from ..verifactu.services.xml_signer import VerifactuXMLSigner
from ..verifactu.services.attachment import VerifactuAttachmentService
from ..verifactu.services.hash_calculator import VerifactuHashCalculator
from ..verifactu.services.logger import VerifactuLogger
from ..verifactu.services.show_notification import VerifactuNotifier
from ..verifactu.services.xml_sender import VerifactuSender
from ..verifactu.services.qr_content import VerifactuQRContentGenerator
from ..verifactu.services.resender import VerifactuResender
from ..verifactu.services.chain_verifier import VerifactuChainVerifier
from ..verifactu.services.event_exporter import VerifactuEventExporter
from ..verifactu.services.hash_verifier import VerifactuHashVerifier
from ..verifactu.services.integrity_verifier import VerifactuIntegrityVerifier
from ..verifactu.services.xml_builder.xml_builder_simple import VerifactuSimpleXMLBuilder
from ..verifactu.services.anomaly_detector import VerifactuAnomalyDetector
from ..verifactu.services.xml_builder.envelope_builder import VerifactuEnvelopeBuilder
from ..verifactu.services.xml_builder.xml_builder_subsanacion import VerifactuXMLBuilderSubsanacion
from ..verifactu.services.xml_builder.xml_builder_anulacion import VerifactuXMLBuilderAnulacion
from ..verifactu.services.xml_builder.envelope_builder_anluacion import (
    VerifactuEnvelopeBuilderAnulacion,
)
from ..verifactu.services.xml_builder.xml_builder_no_verifactu_subsanacion import VerifactuXMLBuilderNoVerifactuSubsanacion
from ..verifactu.services.xml_builder.no_verifactu_xml_builder import VerifactuXMLBuilderNoVerifactu
from ..verifactu.services.xml_builder.xml_builder_no_verifactu_anulacion import VerifactuXMLBuilderNoVerifactuAnulacion
from .invoice.account_move_rectificativa_mixin import AccountMoveRectificativaMixin



_logger = logging.getLogger(__name__)

# ---------- Helpers compatibles 11→18 ----------
def _vf_clean_es(vat):
    vat = (vat or "").strip().upper()
    if vat.startswith("ES"):
        vat = vat[2:]
    return vat.replace(" ", "").replace("-", "").replace(".", "")

# -*- coding: utf-8 -*-
def _vf_get_invoice_date(inv):
    """Odoo 11: devuelve la fecha de factura.
    Prioridad: date_invoice (v11) → invoice_date (si existe por backport) → date (último recurso)."""
    fields_map = getattr(inv, '_fields', {})

    if 'date_invoice' in fields_map:
        v = getattr(inv, 'date_invoice', False)
        if v:
            return v

    if 'invoice_date' in fields_map:  # por si tu base lo trae backport
        v = getattr(inv, 'invoice_date', False)
        if v:
            return v

    # fallback muy defensivo
    return getattr(inv, 'date', False)

# -*- coding: utf-8 -*-
def _vf_is_posted_domain(inv):
    """
    Odoo 11: dominio equivalente a "factura posteada".
    - v13+ (account.move / con move_type): state == 'posted'
    - v10–v12 (account.invoice): state in ('open','paid')
    """
    # Si huele a v13+ (account.move o tiene move_type) -> 'posted'
    try:
        model_name = getattr(inv, '_name', '') or ''
        fields_map = getattr(inv, '_fields', {}) or {}
    except Exception:
        model_name, fields_map = '', {}

    if model_name == 'account.move' or 'move_type' in fields_map:
        return [('state', '=', 'posted')]

    # v10–v12 (account.invoice)
    return [('state', 'in', ('open', 'paid'))]


def _vf_is_customer_doc(inv):
    """Odoo 11: solo facturas de cliente (ventas) y sus abonos.
    Compat: si existe move_type (backports/v13+), úsalo; si no, usa type (v10–12)."""
    fields_map = getattr(inv, '_fields', {})
    if 'move_type' in fields_map:
        raw = getattr(inv, 'move_type', '') or ''
    else:
        raw = getattr(inv, 'type', '') or ''

    # Normaliza a texto y quita espacios (Py2/Py3)
    try:
        basestring  # noqa
        txt = raw.strip() if isinstance(raw, basestring) else unicode(raw)  # noqa: F821
    except NameError:
        txt = raw.strip() if isinstance(raw, str) else str(raw)

    return txt in ('out_invoice', 'out_refund')


# -*- coding: utf-8 -*-
def _get_invoice_date_value(inv):
    """Odoo 11: devuelve la fecha de la factura (normalizada a date si es posible).
    Intenta tu helper _vf_get_invoice_date y, si falla, usa el campo propio
    (v11: 'date_invoice'; compat: si existe 'invoice_date', úsalo)."""
    # 1) Tu helper (si existe)
    try:
        return _vf_get_invoice_date(inv)
    except Exception:
        pass

    # 2) Fallback por campo
    fname = 'invoice_date' if 'invoice_date' in getattr(inv, '_fields', {}) else 'date_invoice'
    val = getattr(inv, fname, False)
    if not val:
        return False

    # 3) Normaliza a date (compatible Py2/Py3)
    try:
        from odoo import fields
        from datetime import datetime as _dt
        try:
            basestring  # Py2 marker
            is_text = isinstance(val, basestring)
        except NameError:
            is_text = isinstance(val, str)

        # datetime -> date
        if hasattr(val, 'date') and not is_text:
            try:
                return val.date()
            except Exception:
                pass

        # ya es date
        if hasattr(val, 'isoformat') and not is_text:
            return val

        # str -> date
        if is_text:
            try:
                return fields.Date.from_string(val)
            except Exception:
                return _dt.strptime(val[:10], "%Y-%m-%d").date()
    except Exception:
        # Si algo falla, devuelve el valor tal cual
        return val

    return val



def _vf_get_move_type(inv):
    """Devuelve 'out_invoice' / 'out_refund' compatible 11→18."""
    # v13+: move_type
    mt = getattr(inv, "move_type", None)
    if mt:
        return mt
    # v11/12: type
    return getattr(inv, "type", "")

# -*- coding: utf-8 -*-
def _vf_display_name(inv):
    """Compat Odoo 11/12: identificador humano para logs/mensajes.

    Prioridad en v11:
      - number (nº de factura al validar)
      - move_name (nombre del asiento, si existe)
      - reference / ref (referencia comercial)
      - origin (documento origen)
      - name (título genérico)
      - fallback: id
    """
    # Py2/Py3 safe str
    try:
        basestring  # noqa
        def _to_text(v):
            if v is None:
                return u""
            try:
                return v.strip() if isinstance(v, basestring) else unicode(v)  # noqa: F821
            except Exception:
                try:
                    return unicode(v)  # noqa: F821
                except Exception:
                    return str(v)
    except NameError:
        def _to_text(v):
            if v is None:
                return ""
            try:
                return v.strip() if isinstance(v, str) else str(v)
            except Exception:
                return str(v)

    for attr in ("number", "move_name", "reference", "ref", "origin", "name"):
        val = getattr(inv, attr, False)
        txt = _to_text(val)
        if txt:
            return txt
    return _to_text(inv.id)


def _vf_get_name(inv):
    """Compat de número/serie."""
    return getattr(inv, "name", None) or getattr(inv, "number", None) or ""

def _vf_get_date(inv):
    """Compat de fecha expedición."""
    return getattr(inv, "invoice_date", None) or getattr(inv, "date_invoice", None)

def _vf_resolve_tipo_factura(inv):
    """Usa tu resolver si está disponible; fallback básico."""
    try:
        # Import local para no romper si no existe en esta base
        from ..verifactu.utils.invoice_type_resolve import VerifactuTipoFacturaResolver
        return VerifactuTipoFacturaResolver.resolve(inv)
    except Exception:
        mt = _vf_get_move_type(inv)
        # F1: normal; R1: rectificativa (fallback simple)
        return "R1" if mt == "out_refund" else "F1"

def _vf_current_id_tuple(inv):
    """Tupla actual (IDEmisor, NumSerie, Fecha(dd-mm-YYYY), TipoFactura)."""
    company_vat = _vf_clean_es(getattr(inv.company_id, "vat", ""))
    num = _vf_get_name(inv)
    d = _vf_get_date(inv)
    fecha = d.strftime("%d-%m-%Y") if d else ""
    tipo = _vf_resolve_tipo_factura(inv)
    return (company_vat, num, bool(d), tipo)

def _vf_last_id_tuple(inv):
    """
    Lee el último snapshot guardado si existe.
    Campos soportados (usa los que tengas; si no, fallback vacío):
      - verifactu_last_id_emisor
      - verifactu_last_num_serie
      - verifactu_last_fecha_bool (o verifactu_last_fecha_str)
      - verifactu_last_tipo_factura
    """
    idemisor = getattr(inv, "verifactu_last_id_emisor", "") or ""
    num = getattr(inv, "verifactu_last_num_serie", "") or ""
    # admitimos bool o string
    fecha_bool = getattr(inv, "verifactu_last_fecha_bool", None)
    if fecha_bool is None:
        fecha_bool = bool(getattr(inv, "verifactu_last_fecha_str", "") or False)
    tipo = getattr(inv, "verifactu_last_tipo_factura", "") or ""
    return (idemisor, num, bool(fecha_bool), tipo)

def _vf_save_id_snapshot(inv):
    """Guarda el snapshot actual si tienes esos campos definidos (silencioso si no)."""
    try:
        idemisor, num, fecha_ok, tipo = _vf_current_id_tuple(inv)
        vals = {}
        if hasattr(inv, "verifactu_last_id_emisor"):
            vals["verifactu_last_id_emisor"] = idemisor
        if hasattr(inv, "verifactu_last_num_serie"):
            vals["verifactu_last_num_serie"] = num
        if hasattr(inv, "verifactu_last_fecha_bool"):
            vals["verifactu_last_fecha_bool"] = fecha_ok
        elif hasattr(inv, "verifactu_last_fecha_str"):
            vals["verifactu_last_fecha_str"] = "1" if fecha_ok else ""
        if hasattr(inv, "verifactu_last_tipo_factura"):
            vals["verifactu_last_tipo_factura"] = tipo
        if vals:
            inv.sudo().with_context(check_move_validity=False).write(vals)
    except Exception:
        _logger.debug("No se pudo guardar snapshot VeriFactu para %s", inv.id)

def _vf_reset_to_pending(inv):
    """Lleva la factura a estado 'pending' para permitir reenvío/recálculo."""
    vals = {
        "verifactu_status": "pending",
        "verifactu_sent": False,
        "verifactu_sent_with_errors": False,
        "verifactu_processed": False,
    }
    # Mantén verifactu_date_sent si quieres histórico; aquí no lo tocamos
    inv.sudo().with_context(check_move_validity=False).write(vals)



class AccountMove(models.Model):
    _inherit = "account.invoice"

    #VARIABLES CRON
    verifactu_processing = fields.Boolean(
        string="Procesando VeriFactu",
        default=False,
        help="Marcado por el CRON/worker para evitar dobles envíos en paralelo."
    )
    verifactu_last_try = fields.Datetime(
        string="Último intento de envío VeriFactu",
        help="Fecha/hora del último intento de envío (lo actualiza CRON/worker)."
    )
    verifactu_retry_count = fields.Integer(
        string="Reintentos VeriFactu",
        default=0,
        help="Número de reintentos realizados (para backoff exponencial)."
    )

    verifactu_last_emisor_nif = fields.Char(readonly=True)
    verifactu_last_numero = fields.Char(readonly=True)
    verifactu_last_fecha = fields.Date(readonly=True)
    verifactu_last_tipo = fields.Char(readonly=True)

    verifactu_detailed_error_msg = fields.Text(
        string="Mensaje de error VeriFactu (en detalle)"
    )

    verifactu_qr = fields.Binary(
        "QR VeriFactu", help="Código QR generado tras la validación VeriFactu."
    )

    verifactu_is_active = fields.Boolean(
        string="VeriFactu Activo",
        compute="_compute_verifactu_is_active",
        store=False,   # pon True si quieres columna persistida en v12
        readonly=True,
        help="Indica si VeriFactu está activo para esta compañía."
    )

    @api.depends('company_id')
    @api.multi
    def _compute_verifactu_is_active(self):
        ConfigEnv = self.env['verifactu.endpoint.config'].sudo()
        has_singleton = hasattr(type(ConfigEnv), 'get_singleton_record') or hasattr(ConfigEnv, 'get_singleton_record')

        for inv in self:
            company = inv.company_id or self.env.user.company_id
            cfg = False
            try:
                if has_singleton:
                    # Preferible si tu modelo lo implementa
                    cfg = ConfigEnv.with_context(force_company=company.id).get_singleton_record()
                else:
                    # Búsqueda estándar por compañía
                    cfg = ConfigEnv.with_context(force_company=company.id).search([('company_id', '=', company.id)], limit=1)
            except Exception:
                # Fallback ultra-defensivo
                cfg = self.env['verifactu.endpoint.config'].sudo().search([('company_id', '=', company.id)], limit=1)

            inv.verifactu_is_active = bool(getattr(cfg, 'verifactu_mode_enabled', False))
    
    verifactu_date_sent = fields.Datetime(
        string="Fecha de envío VeriFactu",
        readonly=True,
        help="Fecha y hora en que se envió la factura a la AEAT mediante VeriFactu.",
    )
    
    verifactu_requerimiento = fields.Char(
        string="Referencia de Requerimiento AEAT",
        help="Código oficial del requerimiento recibido por la AEAT. Obligatorio en el modo No VeriFactu.",
    )
        
    company_id = fields.Many2one(
        'res.company',
        string="Compañía",
        default=lambda self: self.env.user.company_id,
        required=True,
        index=True
    )


    anomaly_cron_enabled = fields.Boolean(
        string="Detección Automática Activa",
        compute="_compute_anomaly_cron_enabled",
        store=False,
    )

    verifactu_sent = fields.Boolean(
        string="Enviado a VeriFactu sin errores", default=False
    )
    verifactu_sent_with_errors = fields.Boolean(
        string="Enviado a VeriFactu con errores", default=False
    )
    verifactu_processed = fields.Boolean(string="VeriFactu procesao", default=False)
    verifactu_status = fields.Selection(
        [
            ("pending", "Pendiente"),
            ("sent", "Enviado"),
            ("accepted_with_errors", "Aceptado con errores"),
            ("error", "Error"),
            ("rejected", "Rechazado"),
            ("canceled", "anulado"),
            ("duplicated", "Duplicado"),  # opcional, si deseas diferenciar
        ],
        default="pending",
        string="Estado VeriFactu",
        tracking=True,
    )

    verifactu_hash_calculated_at = fields.Datetime(
        string="Fecha de Cálculo del Hash", readonly=True
    )

    date_invoice_operation = fields.Date(
        string="Fecha de Operación",
        help="Indica la fecha en la que se realiza la operación económica real si es distinta a la fecha de expedición.",
    )

    verifactu_soap_xml = fields.Binary(string="Verifactu SOAP XML", attachment=False)

    verifactu_generated = fields.Boolean(
        string="XML VeriFactu generado",
        default=False,
        help="Indica si se ha generado el XML para esta factura, aunque no se haya enviado todavía."
    )

    verifactu_error_msg = fields.Text(string="Mensaje de error VeriFactu")
    
    verifactu_dev_hash = fields.Char(string='Verifactu Hash Dev', default='mrrubik:vf-v1.3.20250611', readonly=True)

    verifactu_qr_image = fields.Binary(
        string="VeriFactu QR",
        compute="_compute_verifactu_qr_image",
        store=True,
        attachment=True,
    )
    verifactu_hash = fields.Char(string="Hash VeriFactu", readonly=True)
    verifactu_previous_hash = fields.Char(
        string="Hash Anterior VeriFactu", readonly=True
    )
    verifactu_event_logs = fields.Many2many(
        "verifactu.event.log", string="Registros de Eventos", readonly=True
    )

    verifactu_issued_at = fields.Datetime(string="Fecha y hora de emisión VeriFactu")

    verifactu_base_coste = fields.Monetary(
        string="Base imponible a coste",
        compute="_compute_verifactu_base_coste",
        store=True,
        currency_field='currency_id'
    )
    
    verifactu_status_logs = fields.One2many(
    "verifactu.status.log", "invoice_id",
    string="Historial de Estado VeriFactu",
    )
    
    show_qr_always = fields.Boolean(
        string="Mostrar QR tributario",
        compute="_compute_show_qr_always",
        store=False  # o True si te interesa indexarlo
    )
    
     
# ───────────────────────────────
    # Inicio logica rectificatias
    # ───────────────────────────────
    
    # Campo auxiliar para las vistas (invisible en el XML)
    is_rectificativa_bool = fields.Boolean(
        compute="_compute_is_rectificativa_bool",
        string="¿Es rectificativa?",
        store=False,   # nunca almacenar, siempre calculado
    )

    def _compute_is_rectificativa_bool(self):
        """Sincroniza el campo booleano con el resultado del mixin universal."""
        for rec in self:
            rec.is_rectificativa_bool = AccountMoveRectificativaMixin.is_rectificativa(rec)

    def is_rectificativa(self):
        """API pública para reutilizar desde otras partes del código."""
        return AccountMoveRectificativaMixin.is_rectificativa(self)

    def _reset_verifactu_fields(self, move):
        """Limpia los campos VeriFactu en una factura clonada o rectificativa."""
        vals = {
            "verifactu_status": "pending",
            "verifactu_sent": False,
            "verifactu_sent_with_errors": False,
            "verifactu_generated": False,
            "verifactu_processed": False,
            "verifactu_processing": False,
            "verifactu_retry_count": 0,
            "verifactu_hash": False,
            "verifactu_previous_hash": False,
            "verifactu_qr": False,
            "verifactu_qr_image": False,
            "verifactu_soap_xml": False,
            "verifactu_detailed_error_msg": False,
            "verifactu_error_msg": False,
            "verifactu_requerimiento": False,
            "verifactu_event_logs": [(5, 0, 0)],
            "verifactu_status_logs": [(5, 0, 0)],
            "verifactu_hash_calculated_at": False,
            "verifactu_date_sent": False,
            "verifactu_issued_at": False,
            "verifactu_last_emisor_nif": False,
            "verifactu_last_numero": False,
            "verifactu_last_fecha": False,
            "verifactu_last_tipo": False,
            "verifactu_is_active": True,
        }
        move.write(vals)

    # ───────────────────────────────
    # Compatibilidad Odoo 13+
    # ───────────────────────────────
    def _reverse_moves(self, default_values_list=None, cancel=False):
        moves = super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        for move in moves:
            self._reset_verifactu_fields(move)
        return moves

    # ───────────────────────────────
    # Compatibilidad Odoo ≤12
    # ───────────────────────────────
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        refunds = super(AccountMove, self).refund(
            date_invoice=date_invoice,
            date=date,
            description=description,
            journal_id=journal_id,
        )
        for move in refunds:
            self._reset_verifactu_fields(move)
        return refunds

    # ───────────────────────────────
    # Fin logica rectificatias
    # ───────────────────────────────
    
    def copy(self, default=None):
        """Evita copiar datos VeriFactu al duplicar (compatible Odoo 10–18)."""
        self.ensure_one()
        default = dict(default or {})

        # Valores por defecto "deseados"
        vf_defaults = {
            "verifactu_status": "pending",
            "verifactu_sent": False,
            "verifactu_sent_with_errors": False,
            "verifactu_generated": False,
            "verifactu_processed": False,
            "verifactu_processing": False,
            "verifactu_retry_count": 0,
            "verifactu_hash": False,
            "verifactu_previous_hash": False,
            "verifactu_qr": False,
            "verifactu_qr_image": False,
            "verifactu_soap_xml": False,
            "verifactu_detailed_error_msg": False,
            "verifactu_error_msg": False,
            "verifactu_requerimiento": False,
            "verifactu_event_logs": [(5, 0, 0)],   # limpia one2many/m2m
            "verifactu_status_logs": [(5, 0, 0)],
            "verifactu_hash_calculated_at": False,
            "verifactu_date_sent": False,
            "verifactu_issued_at": False,
            "verifactu_last_emisor_nif": False,
            "verifactu_last_numero": False,
            "verifactu_last_fecha": False,
            "verifactu_last_tipo": False,
            "verifactu_is_active": True,
        }

        # Añade solo campos que existan en este modelo
        for k, v in vf_defaults.items():
            if k in self._fields:
                default.setdefault(k, v)

        # Reinicia el nombre del asiento si venía asignado
        if getattr(self, 'name', False) and self.name != '/':
            default.setdefault('name', '/')

        # ✅ Avanza correctamente en la MRO (compatible Py2/Py3)
        return super(AccountMove, self).copy(default)

    def button_cancel(self):
        """Intercepta el botón Cancelar (todas las versiones Odoo 10–18)."""
        for move in self:
            status = getattr(move, "verifactu_status", None)
            if status in ("sent", "accepted_with_errors"):
                raise UserError(_(
                    "Esta factura ya fue registrada en VeriFactu. "
                    "Antes de cancelarla debes anularla."
                ))

        # Compatibilidad con métodos internos según versión
        if hasattr(super(AccountMove, self), "button_cancel"):
            return super(AccountMove, self).button_cancel()
        elif hasattr(super(AccountMove, self), "action_cancel"):
            return super(AccountMove, self).action_cancel()
        elif hasattr(super(AccountMove, self), "action_invoice_cancel"):
            return super(AccountMove, self).action_invoice_cancel()
        else:
            return True


    @api.depends("company_id")
    def _compute_show_qr_always(self):
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        for move in self:
            move.show_qr_always = config.show_qr_always    

    
    @api.multi
    def _log_verifactu_status(self, status, code=None, notes=u"", update_if_exists=False):
        """Registra un nuevo estado VeriFactu en el historial (v12)."""
        self.ensure_one()
        Log = self.env["verifactu.status.log"].sudo()

        vals = {
            "invoice_id": self.id,
            "status": status,
            "date": getattr(self, "verifactu_hash_calculated_at", False) or fields.Datetime.now(),
            "hash_actual": getattr(self, "verifactu_hash", None),
            "hash_previo": getattr(self, "verifactu_previous_hash", None),
            "notes": notes or u"",
        }

        # Campos opcionales si existen en el modelo de log
        if "aeat_code" in Log._fields:
            vals["aeat_code"] = code or None
        if "xml_soap" in Log._fields:
            vals["xml_soap"] = getattr(self, "verifactu_soap_xml", None)

        if update_if_exists:
            # Intentar actualizar el registro del mismo hash_actual si ya existe
            search_domain = [
                ('invoice_id', '=', self.id),
                ('hash_actual', '=', vals.get('hash_actual')),
            ]
            existing = Log.search(search_domain, limit=1)
            if existing:
                existing.write(vals)
                return existing

        return Log.create(vals)


    @api.depends('invoice_line_ids', 'invoice_line_ids.product_id', 'invoice_line_ids.quantity')
    def _compute_verifactu_base_coste(self):
        for move in self:
            coste_total = 0.0
            for line in move.invoice_line_ids:
                # Si no hay producto o cantidad, se ignora la línea
                if line.product_id and line.quantity:
                    coste_total += line.product_id.standard_price * line.quantity


    def _vf_check_readiness(self, config):
        """
        Devuelve (ok, msgs) indicando si la factura puede generar/enviar a VeriFactu.
        No lanza excepción: solo prepara mensajes.
        """
        msgs = []

        # Config básica
        if not (config and config.cert_pfx and config.cert_password):
            msgs.append("certificado digital no configurado (.pfx + contraseña)")
        if not (config and config.endpoint_url):
            msgs.append("endpoint de VeriFactu no configurado")

        # Licencia (suave: no bloquea, solo avisa)
        try:
            gate_ok = self.env["verifactu.license.gate"]._is_valid()
        except Exception as e:
            gate_ok = False
            msgs.append(f"no se pudo verificar licencia ({e})")

        if not gate_ok:
            msgs.append("licencia no válida o no configurada")

        return (len(msgs) == 0, msgs)
    
    def _vf_log_and_skip(self, msgs, tail=""):
        text = "⚠️ Configuración/licencia incompleta de VeriFactu: " + " | ".join(msgs)
        if tail:
            text += ". %s" % tail
        self.message_post(body=text)

    def _vf_safe_call(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.message_post(body="🛑 Error VeriFactu: %s" % e)
            _logger.exception("Error VeriFactu en %s: %s", getattr(func, "__name__", func), e)
            return None

    def _vf_after_post(self):
        """Bloque común ejecutado tras post/confirm según versión."""
        config = (
            self.env["verifactu.endpoint.config"]
            .sudo()
            .search([("company_id", "=", self.env.user.company_id.id)], limit=1)
        )

        for inv in self:
            # Aviso de updates (no bloqueante)
            try:
                self.env["verifactu.update.checker"].check_and_notify_if_needed(inv)
            except Exception:
                pass

            # Solo ventas cliente (v11/12)
            if getattr(inv, "type", "") != "out_invoice":
                continue

            # Fecha de emisión VeriFactu
            if not getattr(inv, "verifactu_issued_at", False):
                inv.verifactu_issued_at = fields.Datetime.now()

            # Readiness
            ok, msgs = inv._vf_check_readiness(config)
            if not ok:
                inv._vf_log_and_skip(msgs, tail="Ve a Ajustes → VeriFactu para completarla.")
                continue

            # Envío / solo generar
            if inv.should_send_to_verifactu(config):
                inv._vf_safe_call(inv.send_xml)
            else:
                inv._vf_safe_call(inv.only_generate_xml_never_send)

    @api.multi
    def action_invoice_open(self):
        # Ejecuta la validación estándar v12
        res = super(AccountMove, self).action_invoice_open()

        # Config por compañía (v12: sin with_company)
        config = (self.env["verifactu.endpoint.config"]
                    .sudo()
                    .with_context(force_company=self.env.user.company_id.id)
                    .search([("company_id", "=", self.env.user.company_id.id)], limit=1))

        for inv in self:
            # (0) Notificación de actualizaciones (no bloqueante)
            try:
                self.env["verifactu.update.checker"].check_and_notify_if_needed(inv)
            except Exception:
                pass

            # Solo ventas/abonos cliente y ya “posteadas” (v12: open/paid)
            inv_type = getattr(inv, "type", "")
            if inv_type not in ("out_invoice", "out_refund"):
                continue
            if inv.state not in ("open", "paid"):
                continue

            # (1) Diario con VeriFactu deshabilitado → se omite
            journal = getattr(inv, "journal_id", False)
            if journal and not getattr(journal, "verifactu_enabled", True):
                try:
                    from ..verifactu.services.logger import VerifactuLogger
                    VerifactuLogger(inv).log(
                        u"ℹ️ Diario '%s' sin envío VeriFactu habilitado. Se omite." % (journal.name or u"-")
                    )
                except Exception:
                    pass
                # No se genera QR ni se envía ni se calcula hash
                continue

            # (2) Detectar cambio de IDFactura vs snapshot → reset a 'pending'
            try:
                last = _vf_last_id_tuple(inv)
            except Exception:
                last = ("", "", False, "")
            if last != ("", "", False, ""):
                try:
                    curr = _vf_current_id_tuple(inv)
                except Exception:
                    curr = last
                if curr != last:
                    try:
                        from ..verifactu.services.logger import VerifactuLogger
                        VerifactuLogger(inv).log(u"ℹ️ IDFactura cambiado (NIF/Num/Fecha/Tipo) → estado 'pending'.")
                    except Exception:
                        pass
                    try:
                        _vf_reset_to_pending(inv)
                    except Exception:
                        pass

            # (3) Fecha emisión VeriFactu si falta
            if not getattr(inv, "verifactu_issued_at", False):
                inv.verifactu_issued_at = fields.Datetime.now()

            # (4) Readiness (config/licencia/endpoint/certificado)
            try:
                ok, msgs = inv._vf_check_readiness(config)
            except Exception:
                ok, msgs = True, []
            if not ok:
                try:
                    inv._vf_log_and_skip(msgs, tail=u"Ve a Ajustes > VeriFactu para completarla.")
                except Exception:
                    # fallback a chatter
                    try:
                        inv.message_post(body=u"⚠️ Config/licencia VeriFactu incompleta: %s" % u" | ".join(msgs))
                    except Exception:
                        pass
                continue

            # (5) Recalcular QR / Hash (tolerante a errores)
            try:
                from ..verifactu.services.logger import VerifactuLogger
                VerifactuLogger(inv).log(u"ℹ️ Factura validada; recálculo VeriFactu.")
            except Exception:
                pass

            # QR si procede
            if getattr(config, "show_qr_always", False):
                try:
                    from ..verifactu.services.qr_content import VerifactuQRContentGenerator
                    qr_bytes = VerifactuQRContentGenerator(inv, config, factura_verificable=True).generate_qr_binary()
                    inv.verifactu_qr = base64.b64encode(qr_bytes).decode("utf-8") if qr_bytes else False
                except Exception as e:
                    try:
                        from ..verifactu.services.logger import VerifactuLogger
                        VerifactuLogger(inv).log(u"⚠️ Error generando QR: %s" % e)
                    except Exception:
                        pass

            # Hash forzado
            try:
                from ..verifactu.services.hash_calculator import VerifactuHashCalculator
                VerifactuHashCalculator(inv, config).compute_and_update(force_recalculate=True)
            except Exception as e:
                try:
                    from ..verifactu.services.logger import VerifactuLogger
                    VerifactuLogger(inv).log(u"⚠️ Error recalculando hash: %s" % e)
                except Exception:
                    pass

            # (6) Envío / solo generar
            try:
                do_send = inv.should_send_to_verifactu(config)
            except Exception:
                do_send = False
            try:
                if do_send:
                    inv._vf_safe_call(inv.send_xml)
                else:
                    inv._vf_safe_call(inv.only_generate_xml_never_send)
            except Exception:
                # no bloquear validación si el envío falla aquí; ya habrá anomalía/log
                pass

            # (7) Guardar snapshot del IDFactura tras validar
            try:
                _vf_save_id_snapshot(inv)
            except Exception:
                pass

        return res




    def should_send_to_verifactu(self, config):
        return (
            self.type in ("out_invoice", "out_refund") and
            config.auto_send_to_verifactu and
            config.cert_pfx and config.cert_password
        )


    @api.model
    def create(self, vals):
        invoice = super().create(vals)
        return invoice

    def write(self, vals):
        if not vals:
            return super().write(vals)

        res = super().write(vals)

        # v12/v13+: vigila campos que afectan al hash/QR
        critical_fields = {
            'name', 'number',                # v13+ / v12
            'invoice_date', 'date_invoice',  # v13+ / v12
            'amount_total', 'amount_tax',
            'type', 'move_type',             # v12 / v13+
        }
        if not (critical_fields & set(vals.keys())):
            return res

        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)

        for rec in self:
            # Solo facturas de cliente
            inv_type = getattr(rec, 'type', None) or getattr(rec, 'move_type', None)
            if inv_type != 'out_invoice':
                continue

            # "Posteada": v12 => open/paid; v13+ => posted
            state = getattr(rec, 'state', '')
            is_posted = (state in ('open', 'paid')) or (state == 'posted')
            if not is_posted:
                continue

            ok, msgs = rec._vf_check_readiness(config)
            if not ok:
                rec.message_post(body="⚠️ Config/licencia VeriFactu incompleta: {}. Se omite recálculo de QR y hash."
                                    .format(" | ".join(msgs)))
                continue

            # Info en chatter
            rec.message_post(body="ℹ️ Factura modificada; recálculo VeriFactu.")

            # Recalcular QR si procede
            if getattr(config, "show_qr_always", False):
                try:
                    qr_bytes = VerifactuQRContentGenerator(rec, config, factura_verificable=True).generate_qr_binary()
                    rec.verifactu_qr = base64.b64encode(qr_bytes).decode("utf-8") if qr_bytes else False
                except Exception as e:
                    rec.message_post(body=f"⚠️ Error generando QR: {e}")

            # Recalcular hash
            try:
                VerifactuHashCalculator(rec, config).compute_and_update(force_recalculate=True)
            except Exception as e:
                rec.message_post(body=f"⚠️ Error recalculando hash: {e}")

        return res

        
    def open_error_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "verifactu.error.codes.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
            },
        }

    def open_requirement_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "verifactu.requirement.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_ref_requerimiento": self.verifactu_requerimiento or "",
                "active_id": self.id,
            },
        }


    def stop_no_verifactu_mode(self):
        self.verifactu_generated = True
        self.log_system_event("✅ Fin del modo NO VERI*FACTU.Establece de nuevo una url (endoint) de VeriFactu.")
        self.verifactu_is_active = True

        # Vaciar el campo del endpoint de requerimiento si es específico del modo No VeriFactu
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        config.endpoint_url = ""

        msg = "⚠️ Fin del modo NO VERI*FACTU.Establece de nuevo una url (endoint) de VeriFactu."
        VerifactuLogger(self).log(msg)
        
    
    
    def action_open_verifactu_help(self):
        wizard = self.env['verifactu.help.wizard'].create({})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'verifactu.help.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }




    def detect_anomalies(self):
        anomalies = []
        for invoice in self.env["account.invoice"].search(
            [
                ("verifactu_sent", "=", True),
                ("verifactu_sent_with_errors", "=", True),
                ("verifactu_processed", "=", True),
            ]
        ):
            if not self.verify_integrity():
                anomalies.append(invoice)

        # Evento global
        if anomalies:
            msg = f"🛑 Detectadas anomalías en {len(anomalies)} facturas."
            VerifactuLogger(self).log(msg)
        else:
            msg = f"✅ No se detectaron anomalías en los registros de facturación."
            VerifactuLogger(self).log(msg)

    # En account_move.py
    def toggle_anomaly_cron(self):
        detector = VerifactuAnomalyDetector(self.env)
        if detector.is_cron_enabled():
            detector.disable_cron()
        else:
            detector.enable_cron()


    @api.depends()
    def _compute_anomaly_cron_enabled(self):
        # Detecta si el CRON está activo
        cron = self.env.ref(
            "l10n_es_verifactu_POS.ir_cron_detect_anomalies", raise_if_not_found=False
        )
        active = bool(cron and cron.active)
        for record in self:
            record.anomaly_cron_enabled = active

    def export_event_records(self):
        return VerifactuEventExporter(self).export()

    def verify_verifactu_hash(self):
        self.ensure_one()
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        VerifactuHashVerifier(self,config).verify()
        return True

    def verify_verifactu_signature(self):
        self.ensure_one()
        try:
            xml_string = VerifactuSimpleXMLBuilder(self).build()

            # Obtener configuración con el certificado
            config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
            signed_xml = VerifactuXMLSigner(config).sign(xml_string)

            VerifactuLogger(self).log(
                f"✅ Firma electrónica verificada para la factura {self.number}"
            )
            return True

        except Exception as e:
            VerifactuLogger(self).log(
                f"🛑 Error al verificar la firma electrónica: {str(e)}"
            )
            raise UserError(_(f"Error al verificar la firma electrónica: {str(e)}"))

    def verify_integrity(self):
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        return VerifactuIntegrityVerifier(self,config).verify()

    def verify_chain(self):
        return VerifactuChainVerifier(self).verify()

    def log_system_event(self, message):
        event = self.env["verifactu.event.log"].create({"name": message})
        _logger.info(message)
        return event

    def log_backup_restore(self):
        self.log_system_event("🔄 Restauración de copia de seguridad detectada.")

    def log_event_summary(self):
        self.log_system_event("📊 Generación de resumen de eventos.")

    def _generate_verifactu_xml(self):
        return VerifactuSimpleXMLBuilder(self).build()


    @api.depends('state', 'verifactu_status', 'company_id')
    def _compute_verifactu_qr_image(self):
        for rec in self:
            rec.verifactu_qr_image = False

            # v12: 'open' / 'paid' (y soporta v13+ con 'posted')
            is_posted = rec.state in ('open', 'paid', 'posted')
            if not is_posted:
                continue

            # coge la config de la compañía de la factura
            config = (self.env['verifactu.endpoint.config']
                    .sudo()
                    .with_context(company_id=rec.company_id.id)
                    .get_singleton_record())

            should_generate = bool(getattr(config, 'show_qr_always', False)) or \
                rec.verifactu_status in ('sent', 'accepted_with_errors', 'canceled', 'rejected', 'error')
            if not should_generate:
                continue

            # licencia (suave), con contexto de compañía
            gate = self.env['verifactu.license.gate'].with_context(company_id=rec.company_id.id)
            try:
                valid = gate._is_valid() if hasattr(gate, '_is_valid') else gate.ensure_valid(hard=False)
            except Exception:
                valid = False
            if not valid:
                # si quieres log, usa server log aquí; evita chatter en computes
                continue

            # config mínima
            if not (config and config.cert_pfx and config.cert_password and config.endpoint_url):
                continue

            # genera QR (NO .decode() en Binary)
            try:
                qr_bytes = VerifactuQRContentGenerator(rec, config, factura_verificable=True).generate_qr_binary()
                rec.verifactu_qr_image = base64.b64encode(qr_bytes) if qr_bytes else False
            except Exception:
                rec.verifactu_qr_image = False


    def get_verifactu_qr_content(self):
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        return VerifactuQRContentGenerator(self,config,self.verifactu_is_active).generate_content()

    def get_verifactu_qr_image_binary(self):
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        return VerifactuQRContentGenerator(self,config,self.verifactu_is_active).generate_qr_binary()
    
    def only_generate_xml_never_send(self):
        self.ensure_one()

        # 🔐 Restricción: no permitir enviar facturas con fecha anterior a otra ya enviada
        if self.verifactu_is_active:
            newer_sent_invoice = self.search([
                ('id', '!=', self.id),
                ('verifactu_status', 'in', ('sent', 'accepted_with_errors')),
                ('date_invoice', '>', self.date_invoice),
            ], limit=1)

            if newer_sent_invoice:
                raise UserError(_(
                    "No se puede enviar esta factura a VeriFactu porque hay otra factura ya enviada "
                    "con una fecha posterior: %s (%s). Por favor, revisa el orden cronológico de tus facturas."
                ) % (newer_sent_invoice.number, newer_sent_invoice.date_invoice))
                
        """Genera el XML (VeriFactu o No-VeriFactu) sin enviarlo a la AEAT."""
        if self.verifactu_is_active:
            self.prepare_verifactu_record()
        else:
            self.prepare_no_verifactu_record()
            
            
        self._log_verifactu_status(
        "hash_generated",
        notes=_("🧾 Hash y XML SOAP generados correctamente.."),
        update_if_exists=True,
            )

        VerifactuLogger(self).log("📄 XML generado sin envío, lo puedes descargar en la pestaña de VeriFactu")
        self.verifactu_generated = True

    @api.multi
    def send_xml(self):
        """Flujo de envío VeriFactu/No-VeriFactu (compat 10→18, ajustado a v11)."""

        # ---------- Helpers de compat ----------
        def _get_date_field(inv):
            """Nombre del campo fecha de factura según versión."""
            return 'invoice_date' if 'invoice_date' in getattr(inv, '_fields', {}) else 'date_invoice'  # v13+ vs v10–12

        def _get_type_field(inv):
            """Nombre del campo tipo de movimiento según versión."""
            return 'move_type' if 'move_type' in getattr(inv, '_fields', {}) else 'type'  # v13+ vs v10–12

        def _to_date(val):
            """Convierte a date() de forma compatible con v11 (str/date/datetime)."""
            try:
                from datetime import datetime as _dt, date as _d
                if not val:
                    return None
                # datetime -> date
                if hasattr(val, 'date') and not isinstance(val, basestring):
                    try:
                        return val.date()
                    except Exception:
                        pass
                # ya es date
                if hasattr(val, 'isoformat') and not isinstance(val, basestring):
                    return val
                # str -> date
                if isinstance(val, basestring):
                    try:
                        return fields.Date.from_string(val)
                    except Exception:
                        return _dt.strptime(val[:10], "%Y-%m-%d").date()
            except Exception:
                return None
            return None

        def _get_invoice_date_value(inv):
            """Valor de la fecha de factura (usa tu helper si existe)."""
            try:
                return _vf_get_invoice_date(inv)  # tu helper si existe
            except Exception:
                fname = _get_date_field(inv)
                return getattr(inv, fname, False)

        def _last_hash_dt(inv):
            """Último timestamp fiable para comparar 'mismo día' (para _after_activation)."""
            Log = inv.env['verifactu.status.log'].sudo()
            log = Log.search([('invoice_id', '=', inv.id), ('hash_actual', '!=', False)],
                            order='date desc, id desc', limit=1)
            if log and getattr(log, 'date', False):
                try:
                    return fields.Datetime.from_string(log.date)
                except Exception:
                    return log.date
            ts = getattr(inv, 'write_date', None) or getattr(inv, 'create_date', None)
            try:
                return fields.Datetime.from_string(ts) if ts else None
            except Exception:
                return None

        def _after_activation(inv, activation_dt):
            """¿La factura pertenece al periodo VeriFactu (tras activar)? (compat v11)"""
            if not activation_dt:
                return False
            inv_d = _get_invoice_date_value(inv)
            di = _to_date(inv_d)
            da = _to_date(activation_dt)
            if not di or not da:
                return False
            if di > da:
                return True
            if di < da:
                return False
            # mismo día → compara hora real
            rec_ts = _last_hash_dt(inv)
            if rec_ts is None:
                return False
            # normaliza activation_dt a datetime
            try:
                from datetime import datetime as ddt, time as dtime
                act_dt = activation_dt
                if isinstance(act_dt, basestring):
                    try:
                        act_dt = fields.Datetime.from_string(act_dt)
                    except Exception:
                        act_d = _to_date(act_dt)
                        act_dt = ddt.combine(act_d, dtime.min) if act_d else None
                elif hasattr(act_dt, 'isoformat') and not isinstance(act_dt, ddt):
                    act_dt = ddt.combine(act_dt, dtime.min)  # era date
            except Exception:
                act_dt = None
            if not act_dt:
                return False
            return rec_ts >= act_dt

        # ---------------------------------------------------------------------
        # Lógica principal (iteramos: soporta batch y single)
        # ---------------------------------------------------------------------
        Config = self.env['verifactu.endpoint.config'].sudo()
        gate = self.env['verifactu.license.gate']

        for inv in self:
            # 0) Limpia anomalías previas (best-effort)
            try:
                inv._vf_anomaly_clear()
            except Exception:
                pass

            # 1) Config por compañía (v11 no tiene with_company)
            company = inv.company_id or self.env.user.company_id
            config = Config.with_context(force_company=company.id).search([('company_id', '=', company.id)], limit=1)
            activation_dt = getattr(config, 'verifactu_mode_activation_date', False)

            # 2) Licencia
            try:
                license_ok = gate.ensure_valid(hard=False)
            except Exception:
                try:
                    license_ok = gate.sudo().ensure_valid(hard=False)
                except Exception:
                    license_ok = False

            if not license_ok:
                try:
                    inv._vf_anomaly_create('LIC001', _("Licencia inválida o no configurada."), severity='error')
                except Exception:
                    pass
                raise UserError(_("⛔ Licencia de VeriFactu inválida o no configurada.\n"
                                "Introduce tu clave y pulsa 'Obtener/Actualizar token' en Ajustes > VeriFactu."))

            # 3) Reglas legales
            if _vf_is_customer_doc(inv):
                type_field = _get_type_field(inv)
                date_field = _get_date_field(inv)
                inv_date = _get_invoice_date_value(inv)

                # ---------- MODO VERIFACTU (on-line, tras activar) ----------
                if getattr(inv, 'verifactu_is_active', False) and _after_activation(inv, activation_dt):

                    # 3.a) No puede haber YA ENVIADA con fecha posterior
                    newer_domain = [
                        ('id', '!=', inv.id),
                        ('company_id', '=', inv.company_id.id),
                        ('verifactu_status', 'in', ('sent', 'accepted_with_errors')),
                    ] + _vf_is_posted_domain(inv) + [
                        (type_field, 'in', ('out_invoice', 'out_refund')),
                        (date_field, '>', inv_date),
                    ]
                    newer_sent_invoice = inv.sudo().search(newer_domain, limit=1)

                    # (opcional) mismo día pero creada después
                    if (not newer_sent_invoice) and ('create_date' in getattr(inv, '_fields', {}) and inv.create_date):
                        newer_same_day = [
                            ('id', '!=', inv.id),
                            ('company_id', '=', inv.company_id.id),
                            ('verifactu_status', 'in', ('sent', 'accepted_with_errors')),
                        ] + _vf_is_posted_domain(inv) + [
                            (type_field, 'in', ('out_invoice', 'out_refund')),
                            (date_field, '=', inv_date),
                            ('create_date', '>', inv.create_date),
                        ]
                        newer_sent_invoice = inv.sudo().search(newer_same_day, limit=1)

                    if newer_sent_invoice and _after_activation(newer_sent_invoice, activation_dt):
                        try:
                            inv._vf_anomaly_create(
                                'ORD001',
                                _("Existe una factura ya enviada con fecha posterior: %s (%s).") %
                                (_vf_display_name(newer_sent_invoice),
                                _get_invoice_date_value(newer_sent_invoice)),
                                severity='error'
                            )
                        except Exception:
                            pass
                        raise UserError(
                            _("No se puede enviar esta factura porque hay otra ya enviada con fecha posterior: %s (%s).")
                            % (_vf_display_name(newer_sent_invoice), _get_invoice_date_value(newer_sent_invoice))
                        )

                    # 3.b) Encadenamiento: la PREVIA del periodo debe estar enviada/aceptada
                    base_prev_domain = [
                        ('id', '!=', inv.id),
                        ('company_id', '=', inv.company_id.id),
                        ('journal_id', '=', inv.journal_id.id),
                    ] + _vf_is_posted_domain(inv) + [
                        (type_field, 'in', ('out_invoice', 'out_refund')),
                    ]

                    # (1) estrictamente anterior por fecha
                    strict_prev_domain = list(base_prev_domain)
                    strict_prev_domain.append((date_field, '<', inv_date))
                    prev = inv.sudo().search(strict_prev_domain,
                                            order="%s desc, id desc" % date_field, limit=1)

                    # (2) si no hay, misma fecha pero anterior en creación (o id menor)
                    if not prev:
                        same_day_domain = list(base_prev_domain)
                        same_day_domain.append((date_field, '=', inv_date))
                        if 'create_date' in getattr(inv, '_fields', {}) and inv.create_date:
                            same_day_domain_cd = list(same_day_domain)
                            same_day_domain_cd.append(('create_date', '<', inv.create_date))
                            prev = inv.sudo().search(same_day_domain_cd,
                                                    order="create_date desc, id desc", limit=1)
                        if not prev:
                            same_day_domain_id = list(same_day_domain)
                            same_day_domain_id.append(('id', '<', inv.id))
                            prev = inv.sudo().search(same_day_domain_id, order="id desc", limit=1)

                    if prev and _after_activation(prev, activation_dt):
                        if getattr(prev, 'verifactu_is_active', False) and \
                        getattr(prev, 'verifactu_status', '') not in ('sent', 'accepted_with_errors', 'canceled'):
                            try:
                                inv._vf_anomaly_create(
                                    'ORD002',
                                    _("No se puede enviar esta factura (%s) porque la anterior (%s), ya en periodo VeriFactu, "
                                    "aún no ha sido enviada o tiene errores.") %
                                    (_vf_display_name(inv), _vf_display_name(prev)),
                                    severity='error'
                                )
                            except Exception:
                                pass
                            raise UserError(
                                _("⛔ Encadenamiento VeriFactu roto.\n"
                                "La factura anterior (%s), ya del periodo VeriFactu, no está enviada.")
                                % (_vf_display_name(prev))
                            )

                # ---------- MODO NO-VERIFACTU o antes de activar ----------
                # (no se bloquea por encadenamiento en v11: la cadena es interna)
                pass

            # 4) Config mínima
            missing_cert = not (config and getattr(config, 'cert_pfx', False) and getattr(config, 'cert_password', False))
            endpoint_url = (getattr(config, 'endpoint_url', '') or '').strip()
            missing_endpoint = not (config and endpoint_url)
            if missing_cert or missing_endpoint:
                try:
                    if missing_cert:
                        inv._vf_anomaly_create('CFG001', _("Certificado PFX/contraseña no configurados."), severity='error')
                    if missing_endpoint:
                        inv._vf_anomaly_create('CFG002', _("Endpoint VeriFactu no configurado."), severity='error')
                except Exception:
                    pass
            human_msg = " | ".join(filter(None, [
                _("certificado digital no configurado (.pfx + contraseña)") if missing_cert else "",
                _("endpoint de VeriFactu no configurado") if missing_endpoint else "",
            ]))
            if human_msg:
                raise UserError(_("No se puede enviar la factura: %s.") % human_msg)

            # 5) Modo No VeriFactu → requiere 'código de requerimiento'
            if not getattr(inv, 'verifactu_is_active', False):
                req_code = (getattr(inv, 'verifactu_requerimiento', '') or '').strip()
                if not req_code:
                    try:
                        inv._vf_anomaly_create('REQ001', _("Modo No VeriFactu sin código de requerimiento informado."),
                                            severity='error')
                    except Exception:
                        pass
                    raise UserError(
                        _("Esta factura está en modo 'No VeriFactu' y el envío se realiza por requerimiento.\n"
                        "Indica primero el 'Código de requerimiento' en la pestaña VeriFactu de esta factura.")
                    )

            # 6) Flujo de generación + envío (idempotente)
            is_generated = bool(getattr(inv, 'verifactu_generated', False))
            status = getattr(inv, 'verifactu_status', '') or ''
            is_pending = (status == 'pending')

            if is_generated and is_pending:
                if getattr(inv, 'verifactu_is_active', False):
                    inv.send_verifactu_record()
                else:
                    inv.send_no_verifactu_record()
            else:
                if getattr(inv, 'verifactu_is_active', False):
                    inv.prepare_verifactu_record()
                    inv.send_verifactu_record()
                else:
                    inv.prepare_no_verifactu_record()
                    inv.send_no_verifactu_record()

            if 'verifactu_generated' in getattr(inv, '_fields', {}):
                inv.verifactu_generated = True

        return True

    
    def prepare_no_verifactu_record(self):
        self.ensure_one()


        self._validate_verifactu_tax_rates()
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)

        VerifactuHashCalculator(self, config).compute_and_update(force_recalculate=True)

        builder = VerifactuXMLBuilderNoVerifactu(self, config)

        raw_xml = builder.build()

        self.verifactu_soap_xml = base64.b64encode(raw_xml.encode("utf-8"))

        # Adjuntar pero no enviar aún
        VerifactuAttachmentService(self).attach_xml(raw_xml)


    
    def send_no_verifactu_record(self):
        self.ensure_one()

        if not self.verifactu_soap_xml:
            raise UserError(_("No se ha generado el XML. Ejecuta primero 'prepare_no_verifactu_record()'."))

        decoded_xml = base64.b64decode(self.verifactu_soap_xml).decode("utf-8")
        attachment = VerifactuAttachmentService(self).attach_xml(decoded_xml)

        VerifactuSender(self).send(decoded_xml, attachment)



    def prepare_verifactu_record(self):
        self.ensure_one()

        self._validate_verifactu_tax_rates()
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)

        VerifactuHashCalculator(self, config).compute_and_update(force_recalculate=True)

        # Selección de builder
        builder = VerifactuXMLBuilder(self, config)

        raw_xml = builder.build()
        signed_xml = raw_xml  # Omitida la firma

        soap_envelope = VerifactuEnvelopeBuilder(self, config=config).build(signed_xml)
        self.verifactu_soap_xml = base64.b64encode(soap_envelope.encode("utf-8"))

        qr_base64 = base64.b64encode(
            VerifactuQRContentGenerator(self, config, self.verifactu_is_active).generate_qr_binary()
        ).decode("utf-8")
        self.verifactu_qr = qr_base64

        # Adjuntar, pero sin enviar aún
        VerifactuAttachmentService(self).attach_xml(soap_envelope)



    def send_verifactu_record(self):
        self.ensure_one()

        if not self.verifactu_soap_xml:
            raise UserError(_("No se ha generado el XML. Ejecuta primero 'prepare_verifactu_record()'."))

        decoded_envelope = base64.b64decode(self.verifactu_soap_xml).decode("utf-8")
        attachment = VerifactuAttachmentService(self).attach_xml(decoded_envelope)

        VerifactuSender(self).send(decoded_envelope, attachment)

    def generate_verifactu_anulacion(self):
        self.ensure_one()


        self._validate_verifactu_tax_rates()
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)

        # 1. Calcular el hash y guardarlo
        hash_value = VerifactuHashCalculator(self,config).compute_cancellation_hash()
        self.verifactu_hash = hash_value

        # 2. Seleccionar el builder según si es subsanación o no

        if self.verifactu_is_active:

                if self.verifactu_status == "pending":
                    builder = VerifactuXMLBuilderAnulacion(self, config)
    
        else:
                if self.verifactu_status == "pending":
                    builder = VerifactuXMLBuilderNoVerifactuAnulacion(self, config)

        # 3. Construir el XML
        raw_xml = builder.build()

        # 4. Firmar el XML
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        # signed_xml = VerifactuXMLSigner(config).sign(raw_xml)

        # Omitir la firma
        signed_xml = raw_xml

        # Envolver el XML sin firma
        soap_envelope = VerifactuEnvelopeBuilderAnulacion(self, config=config).build(signed_xml)

        # 6. Generar y guardar el QR
        qr_base64 = base64.b64encode(
            VerifactuQRContentGenerator(self,config,self.verifactu_is_active).generate_qr_binary()
        ).decode("utf-8")
        self.verifactu_qr = qr_base64

        # 7. Envolver en sobre SOAP
        soap_envelope = VerifactuEnvelopeBuilderAnulacion(self, config=config).build(
            signed_xml
        )
        self.verifactu_soap_xml = base64.b64encode(soap_envelope.encode("utf-8"))
        
        # 🔁 Nuevo paso 8: Adjuntar el XML **ya envuelto en SOAP**
        xml_attachment = VerifactuAttachmentService(self).attach_xml(soap_envelope)

        # 8. Enviar el XML
        VerifactuSender(self).send(soap_envelope, xml_attachment)

        # 9. Log final
        if self.verifactu_status == "sent":
            builder = VerifactuXMLBuilderAnulacion(self, config)
            VerifactuLogger(self).log("✅ Factura VeriFactu anulada correctamente")
            verifactu_status= "canceled"
        elif self.verifactu_status == "accepted_with_errors":
            builder = VerifactuXMLBuilderAnulacion(self, config)
            VerifactuLogger(self).log(
                "✅ Factura VeriFactu anulada correctamente con errores"
            )
            verifactu_status= "canceled"
        elif self.verifactu_status == "rejected":
            builder = VerifactuXMLBuilderAnulacion(self, config, rechazo_previo=True)
            VerifactuLogger(self).log(
                "🛑 ESte VeriFactu XML de anulacion ha sido rechazado, mira la ventana de error"
            )
        elif self.verifactu_status == "error":
            builder = VerifactuXMLBuilderAnulacion(self, config, rechazo_previo=True)
            VerifactuLogger(self).log(
                "🛑 Error al anular la factura verifactu por favor revisa el error detallado"
            )
        else:
            builder = VerifactuXMLBuilderAnulacion(self, config)
            VerifactuLogger(self).log("✅ Factura VeriFactu anulada correctamente")
            verifactu_status= "canceled"
        return True

    def _validate_before_generation(self):
        if self.state != "posted":
            raise UserError(_("🛑 Intento de procesar factura no confirmada."))

        if self.tye not in ("out_invoice", "out_refund"):
            raise UserError(
                _("🛑 Solo se pueden procesar facturas de cliente o rectificativas.")
            )

    def _ensure_verifactu_hash(self):
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        if self.type == "out_refund" or not self.verifactu_hash:
            self.verifactu_hash = VerifactuHashCalculator(self,config).compute_hash(
                force_recalculate=True
            )

    def build_verifactu_xml(self):
        return VerifactuXMLBuilder(self).build()

    def _attach_signed_verifactu_xml(self, signed_xml):
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"verifactu_{self.number.replace('/', '_')}.xml",
                "type": "binary",
                "res_model": "account.invoice",
                "res_id": self.id,
                "datas": base64.b64encode(signed_xml.encode("utf-8")),
                "mimetype": "application/xml",
            }
        )
        return attachment

    def send_verifactu(self, signed_xml_str, attachment):
        return VerifactuSender(self).send(signed_xml_str, attachment)

    def view_verifactu_error(self):
        raise UserError(
            _(
                self.verifactu_detailed_error_msg
                or _("No hay mensaje de error detallado registrado.")
            )
        )

    def resend_verifactu(self):
        return VerifactuResender(self).resend()

    def open_verifactu_xml(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/verifactu/download/{self.id}",
            "target": "new",
        }

    def open_verifactu_soap_xml(self):
        self.ensure_one()
        if not self.verifactu_soap_xml:
            raise UserError(_("El archivo SOAP no está disponible."))

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/verifactu_soap_xml/soap_envelope.xml?download=true",
            "target": "new",
        }

    def open_verifactu_qr(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/verifactu/download_qr/{self.id}",
            "target": "new",
        }

    def _get_system_info(self):
        # Datos del sistema informático
        system_name = platform.node()
        system_id = hashlib.sha256(socket.gethostname().encode("utf-8")).hexdigest()[:8]
        system_version = platform.version()
        installation_id = hashlib.sha256(
            (system_name + system_id).encode("utf-8")
        ).hexdigest()[:8]
        multi_ot = "S" if len(self.env["res.company"].sudo().search([])) > 1 else "N"

        return {
            "NombreSistemaInformatico": system_name,
            "IdSistemaInformatico": system_id,
            "Version": system_version,
            "NumeroInstalacion": installation_id,
            "TipoUsoPosibleSoloVerifactu": "S",
            "TipoUsoPosibleOtros": "N",
            "TipoUsoPosibleMultiOT": multi_ot,
        }

    def _is_valid_nif(self, nif):
        """Valida que el NIF tenga un formato básico correcto (8–9 caracteres alfanuméricos)"""
        return bool(re.match(r"^[A-Z0-9]{8,9}$", nif or ""))

    def _validate_verifactu_tax_rates(self):
        valid_tax_rates = {"0", "4", "5", "7", "10", "21"}

        def _iter_percent_taxes(tax):
            """Desglosa impuestos de grupo y deja solo los percentuales."""
            amount_type = getattr(tax, 'amount_type', None) or getattr(tax, 'type', None)
            if amount_type == 'group' and getattr(tax, 'children_tax_ids', False):
                for child in tax.children_tax_ids:
                    for t in _iter_percent_taxes(child):
                        yield t
            else:
                yield tax

        for inv in self:
            for line in inv.invoice_line_ids:
                # v12: invoice_line_tax_ids ; v13+: tax_ids
                taxes = line.invoice_line_tax_ids if 'invoice_line_tax_ids' in line._fields else line.tax_ids
                for tax in taxes:
                    for t in _iter_percent_taxes(tax):
                        amount_type = getattr(t, 'amount_type', None) or getattr(t, 'type', None)
                        if amount_type != 'percent':
                            # Ignora impuestos fijos/división para esta validación
                            continue
                        rate = float(getattr(t, 'amount', 0.0))
                        rate_str = str(int(round(abs(rate))))
                        if rate_str not in valid_tax_rates:
                            prod = getattr(line, 'product_id', False)
                            line_label = (getattr(prod, 'display_name', None) or line.name or "/")
                            raise UserError(
                                _("Tipo de IVA no válido para VeriFactu: %s%% en la línea '%s'. "
                                "Solo se permiten los tipos: %s.")
                                % (rate_str, line_label, ", ".join(sorted(valid_tax_rates)))
                            )
                            

    @api.multi
    def _vf_anomaly_create(self, code, message, severity='error'):
        A = self.env['verifactu.anomaly'].sudo()
        for inv in self:
            company = getattr(inv, 'company_id', self.env.user.company_id)
            user = self.env.user
            code_str = (code or '').strip().upper()

            # Mapeo simple code -> anomaly_type
            if code_str.startswith('ORD'):
                a_type = 'out_of_order'
            elif code_str.startswith('STA'):     # por si en algún sitio generas "STA..." para stale
                a_type = 'stale_pending'
            else:
                a_type = 'generic'               # LICxxx, CFGxxx, REQxxx, etc.

            vals = {
                'move_id': inv.id,
                'company_id': company.id if company else False,
                'code': code_str,
                'anomaly_type': a_type,
                'message': message or '',
                'severity': (severity or 'error'),
                'detected_at': fields.Datetime.now(),
                'detected_by': user.id if user else False,
            }

            # Purga defensiva por si tu tabla no tiene alguno (aunque en el modelo de arriba sí los hemos añadido):
            for k in list(vals.keys()):
                if k not in A._fields:
                    vals.pop(k)

            # Normaliza severidad si es selección
            if 'severity' in vals and 'severity' in A._fields:
                selection = A._fields['severity'].selection or []
                allowed = [s[0] for s in selection]
                if allowed and vals['severity'] not in allowed:
                    vals['severity'] = allowed[0]

            A.create(vals)


    @api.multi
    def _vf_anomaly_clear(self):
        """Elimina anomalías previas de estas facturas (v12)."""
        A = self.env['verifactu.anomaly'].sudo()
        for inv in self:
            A.search([('move_id', '=', inv.id)]).unlink()