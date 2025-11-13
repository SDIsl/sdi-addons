# -*- coding: utf-8 -*-
# models/verifactu_endpoint_config.py
# Desarrollado por Juan Ormaechea (Mr. Rubik) — Odoo Proprietary License v1.0

import logging
import base64
import re
from datetime import timedelta

from odoo import models, fields, api, release, _
from odoo.exceptions import ValidationError, UserError

from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


# -------------------------------
# Helpers de compatibilidad v12
# -------------------------------
def _get_company(env):
    """Compat v10–v12 con soporte de force_company en el contexto."""
    cid = env.context.get('force_company') or env.user.company_id.id
    return env['res.company'].browse(int(cid))



def _is_modern(env):
    """Odoo 13+ → display_notification disponible (en v12: False)."""
    try:
        major = int(str(getattr(release, 'major_version', '') or release.version).split('.')[0])
    except Exception:
        major = 12
    return major >= 13


def _notify_success(env, title, message, sticky=False):
    if _is_modern(env):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message, 'type': 'success', 'sticky': bool(sticky)},
        }
    # ≤ Odoo 12 → rainbow man
    return {'effect': {'fadeout': 'slow', 'message': u"%s\n%s" % (title or '', message or ''), 'type': 'rainbow_man'}}


def _notify_error(env, title, message, sticky=True):
    if _is_modern(env):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message, 'type': 'danger', 'sticky': bool(sticky)},
        }
    # ≤ Odoo 12 → error modal
    raise UserError(u"%s\n%s" % (title or _("Error"), message or ""))


# --------------------------------------------
# Modelo persistente de configuración (v12)
# --------------------------------------------
class VerifactuEndpointConfig(models.Model):
    _name = 'verifactu.endpoint.config'
    _description = 'Configuración persistente del Endpoint VeriFactu'
    _rec_name = 'endpoint_url'
    
    _sql_constraints = [
        ('verifactu_cfg_company_uniq',
        'unique(company_id)',
        'Ya existe una configuración VeriFactu para esta compañía.')
    ]

    # Ajustes generales
    anomaly_cron_enabled = fields.Boolean(
        string="Activar detección global de anomalías", default=False)
    anomaly_stale_days = fields.Integer(
        string="Días para considerar 'estancada'", default=7)
    anomaly_make_activity = fields.Boolean(
        string="Crear actividad de revisión", default=False)

    endpoint_url = fields.Char("URL del endpoint de VeriFactu", default="")
    # Producción AEAT (referencia): https://prewww1.aeat.es/wlpl/TIKE-CONT/ws/SistemaFacturacion/VerifactuSOAP

    # Certificado
    cert_pfx = fields.Binary("Certificado PFX", attachment=True)
    cert_pfx_filename = fields.Char("Nombre del archivo PFX")
    # OJO: no usar password=True aquí; va en la VISTA XML.
    cert_password = fields.Char(string="Contraseña del certificado")

    company_id = fields.Many2one(
        'res.company',
        string="Compañía",
        default=lambda self: _get_company(self.env),
        required=True,
        index=True,
    )

    show_qr_always = fields.Boolean(
        string="Mostrar siempre el QR en la factura",
        default=True,
        help="Si está activado, el código QR se incluirá en todas las facturas, incluso si no se envían a la AEAT."
    )

    # --- Toggles de envío automático ---
    cron_auto_send_enabled = fields.Boolean(
        string="Activar envío automático periódico",
        default=False,
        help="Si está activado, se enviarán automáticamente las facturas pendientes a VeriFactu mediante el cron."
    )
    auto_send_to_verifactu = fields.Boolean(
        string="Enviar automáticamente a VeriFactu al confirmar",
        default=False,
        help="Si está activo, las facturas se enviarán automáticamente a VeriFactu al validar."
    )

    # --- Parámetros del CRON / backoff / rate-limit (periódico, por compañía) ---
    cron_batch_size = fields.Integer(
        string="Tamaño de lote (batch)",
        default=5,
        help="Máximo de facturas por pasada del cron."
    )
    retry_backoff_min = fields.Integer(
        string="Backoff base (min)",
        default=10,
        help="Minutos hasta el primer reintento; luego crece exponencialmente."
    )
    retry_backoff_cap_min = fields.Integer(
        string="Backoff tope (min)",
        default=60,
        help="Tope máximo de espera entre reintentos por factura."
    )
    request_min_interval_sec = fields.Integer(
        string="Intervalo mínimo entre envíos (s)",
        default=60,
        help="Margen mínimo entre peticiones al portal (rate-limit por compañía)."
    )

    # --- Envío diario a una hora fija (por compañía) ---
    daily_auto_send_enabled = fields.Boolean(
        string="Activar envío diario a una hora",
        default=False,
        help="Si está activado, se ejecutará un cron diario a la hora indicada (hora local de la compañía)."
    )
    daily_send_time = fields.Char(
        string="Hora diaria (HH:MM)",
        default="03:00",
        help="Formato 24h HH:MM. Ej.: 03:00, 14:30."
    )

    # --- Parámetros PROPIOS del cron diario (independientes del periódico) ---
    daily_use_custom_params = fields.Boolean(
        string="Usar parámetros propios en el envío diario",
        default=False,
        help="Si está activo, el cron diario usará estos parámetros en lugar de los del cron periódico."
    )
    daily_cron_batch_size = fields.Integer(
        string="Tamaño de lote (diario)",
        default=5,
        help="Máximo de facturas por pasada del cron diario."
    )
    daily_retry_backoff_min = fields.Integer(
        string="Backoff base (min) diario",
        default=10,
        help="Minutos para el primer reintento en el cron diario; luego crece exponencialmente."
    )
    daily_retry_backoff_cap_min = fields.Integer(
        string="Backoff tope (min) diario",
        default=60,
        help="Tope máximo de espera entre reintentos por factura en el cron diario."
    )
    daily_request_min_interval_sec = fields.Integer(
        string="Intervalo mínimo entre envíos (s) diario",
        default=60,
        help="Margen mínimo entre peticiones al portal por compañía en el cron diario (rate-limit)."
    )

    # Información del Sistema Informático
    verifactu_system_name = fields.Char(string="Nombre del sistema informático")
    verifactu_system_id = fields.Char(string="ID del sistema")
    verifactu_system_version = fields.Char(string="Versión")
    verifactu_system_installation_number = fields.Char(string="Número de instalación")
    verifactu_system_use_only_verifactu = fields.Selection(
        selection=[('S', 'Sí'), ('N', 'No')], string="Solo se usa para VeriFactu"
    )
    verifactu_system_multi_ot = fields.Selection(
        selection=[('S', 'Sí'), ('N', 'No')], string="Múltiples OT"
    )
    verifactu_system_multiple_ot_indicator = fields.Selection(
        selection=[('S', 'Sí'), ('N', 'No')], string="Indicador de múltiples OT"
    )

    # Modo VeriFactu / No VeriFactu
    verifactu_mode_enabled = fields.Boolean(
        string="Modo VeriFactu",
        default=False,
        help="Activa el envío directo de facturas al sistema VeriFactu."
    )
    no_verifactu_mode_enabled = fields.Boolean(
        string="Modo No VeriFactu",
        default=False,
        help="Activa el modo de remisión bajo requerimiento."
    )
    verifactu_mode_activation_date = fields.Datetime(
        string="Fecha de activación del modo actual"
    )
    last_verifactu_mode = fields.Selection(
        [('verifactu', 'VeriFactu'), ('no_verifactu', 'No VeriFactu')],
        string="Último modo activo"
    )

    verifactu_update_link = fields.Char(
        string="Link descarga actualización", readonly=True,
        default="https://mrrubik.com/descargas/verifactu/modules/v11HGJKMNBPOS/l10n_es_verifactu_POS.zip"
    )
    


    # -----------------------
    # Validaciones de parámetros del cron
    # -----------------------
    @api.constrains(
        'cron_batch_size', 'retry_backoff_min', 'retry_backoff_cap_min',
        'request_min_interval_sec', 'daily_send_time',
        'daily_cron_batch_size', 'daily_retry_backoff_min',
        'daily_retry_backoff_cap_min', 'daily_request_min_interval_sec'
    )
    def _check_cron_params(self):
        for rec in self:
            # Saneo de enteros (periódico)
            if rec.cron_batch_size and rec.cron_batch_size < 1:
                rec.cron_batch_size = 1
            if rec.retry_backoff_min and rec.retry_backoff_min < 1:
                rec.retry_backoff_min = 1
            if rec.retry_backoff_cap_min and rec.retry_backoff_cap_min < rec.retry_backoff_min:
                rec.retry_backoff_cap_min = rec.retry_backoff_min
            if rec.request_min_interval_sec and rec.request_min_interval_sec < 0:
                rec.request_min_interval_sec = 0

            # Saneo de enteros (diario, si usa custom)
            if rec.daily_use_custom_params:
                if rec.daily_cron_batch_size and rec.daily_cron_batch_size < 1:
                    rec.daily_cron_batch_size = 1
                if rec.daily_retry_backoff_min and rec.daily_retry_backoff_min < 1:
                    rec.daily_retry_backoff_min = 1
                if (rec.daily_retry_backoff_cap_min and
                        rec.daily_retry_backoff_cap_min < rec.daily_retry_backoff_min):
                    rec.daily_retry_backoff_cap_min = rec.daily_retry_backoff_min
                if rec.daily_request_min_interval_sec and rec.daily_request_min_interval_sec < 0:
                    rec.daily_request_min_interval_sec = 0

            # Validación de hora diaria si el feature está activo
            if rec.daily_auto_send_enabled:
                t = (rec.daily_send_time or "").strip()
                if not t:
                    raise ValidationError(_("Debes indicar una hora diaria en formato HH:MM."))
                if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", t):
                    raise ValidationError(_("La hora diaria debe tener formato 24h HH:MM, p. ej. 03:00 o 14:30."))

    # -----------------------
    # Carga por defecto (singleton por compañía)
    # -----------------------
    @api.model
    def default_get(self, fields_list):
        if self.env.context.get('no_default'):
            return super(VerifactuEndpointConfig, self).default_get(fields_list)

        config = self.get_singleton_record()
        res = super(VerifactuEndpointConfig, self).default_get(fields_list)

        vals = {
            'endpoint_url': config.endpoint_url,
            'cert_pfx': config.cert_pfx,
            'cert_pfx_filename': config.cert_pfx_filename,
            'cert_password': config.cert_password,
            'show_qr_always': config.show_qr_always,
            'auto_send_to_verifactu': config.auto_send_to_verifactu,
            'cron_auto_send_enabled': config.cron_auto_send_enabled,
            'cron_batch_size': config.cron_batch_size,
            'retry_backoff_min': config.retry_backoff_min,
            'retry_backoff_cap_min': config.retry_backoff_cap_min,
            'request_min_interval_sec': config.request_min_interval_sec,
            # nuevos (envío diario)
            'daily_auto_send_enabled': config.daily_auto_send_enabled,
            'daily_send_time': config.daily_send_time,
            'daily_use_custom_params': config.daily_use_custom_params,
            'daily_cron_batch_size': config.daily_cron_batch_size,
            'daily_retry_backoff_min': config.daily_retry_backoff_min,
            'daily_retry_backoff_cap_min': config.daily_retry_backoff_cap_min,
            'daily_request_min_interval_sec': config.daily_request_min_interval_sec,
            # sistema informático
            'verifactu_system_name': config.verifactu_system_name,
            'verifactu_system_id': config.verifactu_system_id,
            'verifactu_system_version': config.verifactu_system_version,
            'verifactu_system_installation_number': config.verifactu_system_installation_number,
            'verifactu_system_use_only_verifactu': config.verifactu_system_use_only_verifactu,
            'verifactu_system_multi_ot': config.verifactu_system_multi_ot,
            'verifactu_system_multiple_ot_indicator': config.verifactu_system_multiple_ot_indicator,
            # modo emisión
            'verifactu_mode_enabled': config.verifactu_mode_enabled,
            'no_verifactu_mode_enabled': config.no_verifactu_mode_enabled,
            'last_verifactu_mode': config.last_verifactu_mode,
            'verifactu_mode_activation_date': config.verifactu_mode_activation_date,
        }
        for k in list(vals.keys()):
            if k not in fields_list:
                vals.pop(k)
        res.update(vals)

        logger.info("📂 Datos del singleton cargados en el formulario")
        return res

    @api.model
    def get_singleton_record(self):
        company = _get_company(self.env)
        config = self.sudo().search([('company_id', '=', company.id)], limit=1)
        if not config:
            config = self.sudo().with_context(no_default=True).create({
                'company_id': company.id,
                'endpoint_url': '',
                'cert_pfx_filename': '',
                'cert_password': '',
                'show_qr_always': True,
                'auto_send_to_verifactu': False,
                'cron_auto_send_enabled': False,
                'cron_batch_size': 5,
                'retry_backoff_min': 10,
                'retry_backoff_cap_min': 60,
                'request_min_interval_sec': 60,
                # nuevos por defecto de envío diario
                'daily_auto_send_enabled': False,
                'daily_send_time': '03:00',
                'daily_use_custom_params': False,
                'daily_cron_batch_size': 5,
                'daily_retry_backoff_min': 10,
                'daily_retry_backoff_cap_min': 60,
                'daily_request_min_interval_sec': 60,
                # modo VeriFactu / No VeriFactu (por defecto → No VeriFactu)
                'verifactu_mode_enabled': False,
                'no_verifactu_mode_enabled': True,
                'last_verifactu_mode': 'no_verifactu',
                'verifactu_mode_activation_date': fields.Datetime.now(),
            })
            logger.info("🆕 Registro singleton creado para VeriFactu (%s)", company.name)
        return config

    # -----------------------
    # Onchange
    # -----------------------
    @api.onchange('cert_pfx')
    def _onchange_cert_pfx(self):
        if self.cert_pfx and not self.cert_pfx_filename:
            filename = self._context.get('filename') or 'certificado.pfx'
            self.cert_pfx_filename = filename
            logger.info("📁 Archivo PFX cargado: %s", filename)

    # -----------------------
    # Acciones (botones)
    # -----------------------
    def _validate_endpoint(self):
        if self.endpoint_url:
            url = (self.endpoint_url or '').strip()
            if not url.lower().startswith('https://'):
                logger.error("URL inválida: %s", url)
                raise ValidationError(_("La URL debe comenzar por 'https://' y ser válida."))
            self.endpoint_url = url

    def _normalize_daily_time(self, time_str):
        """Normaliza ' 3:5 ' -> '03:05'. Devuelve None si no válida."""
        t = (time_str or "").strip()
        m = re.match(r"^(\d{1,2}):(\d{1,2})$", t)
        if not m:
            return None
        hh = int(m.group(1))
        mm = int(m.group(2))
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return "%02d:%02d" % (hh, mm)
        return None

    @api.multi
    def save_config(self):
        self.ensure_one()
        self._validate_endpoint()

        # normalización/validación de hora diaria si el toggle está activo
        daily_enabled = bool(self.daily_auto_send_enabled)
        daily_time = self.daily_send_time
        if daily_enabled:
            norm = self._normalize_daily_time(daily_time)
            if not norm:
                raise ValidationError(_("La hora diaria debe tener formato 24h HH:MM, p. ej. 03:00 o 14:30."))
            daily_time = norm
        else:
            daily_time = self.daily_send_time or "03:00"

        if self.cert_pfx and not self.cert_pfx_filename:
            self.cert_pfx_filename = 'certificado.pfx'
            logger.info("🔐 Certificado PFX asignado: %s", self.cert_pfx_filename)

        singleton = self.get_singleton_record()
        singleton.write({
            'endpoint_url': self.endpoint_url,
            'cert_pfx': self.cert_pfx,
            'cert_pfx_filename': self.cert_pfx_filename,
            'cert_password': self.cert_password,
            'show_qr_always': self.show_qr_always,
            'auto_send_to_verifactu': self.auto_send_to_verifactu,
            'cron_auto_send_enabled': self.cron_auto_send_enabled,
            'cron_batch_size': self.cron_batch_size or 5,
            'retry_backoff_min': self.retry_backoff_min or 10,
            'retry_backoff_cap_min': self.retry_backoff_cap_min or 60,
            'request_min_interval_sec': self.request_min_interval_sec or 60,
            # nuevos (envío diario)
            'daily_auto_send_enabled': daily_enabled,
            'daily_send_time': daily_time,
            'daily_use_custom_params': bool(self.daily_use_custom_params),
            'daily_cron_batch_size': self.daily_cron_batch_size or 5,
            'daily_retry_backoff_min': self.daily_retry_backoff_min or 10,
            'daily_retry_backoff_cap_min': self.daily_retry_backoff_cap_min or 60,
            'daily_request_min_interval_sec': self.daily_request_min_interval_sec or 60,
            # sistema informático
            'verifactu_system_name': self.verifactu_system_name,
            'verifactu_system_id': self.verifactu_system_id,
            'verifactu_system_version': self.verifactu_system_version,
            'verifactu_system_installation_number': self.verifactu_system_installation_number,
            'verifactu_system_use_only_verifactu': self.verifactu_system_use_only_verifactu,
            'verifactu_system_multi_ot': self.verifactu_system_multi_ot,
            'verifactu_system_multiple_ot_indicator': self.verifactu_system_multiple_ot_indicator,
            # modo emisión
            'verifactu_mode_enabled': self.verifactu_mode_enabled,
            'no_verifactu_mode_enabled': self.no_verifactu_mode_enabled,
            'last_verifactu_mode': self.last_verifactu_mode,
            'verifactu_mode_activation_date': self.verifactu_mode_activation_date,
        })

        return _notify_success(self.env, '✅ Configuración guardada', _('Los datos han sido guardados correctamente.'))

    @api.multi
    def action_reset_certificate(self):
        self.ensure_one()
        self.write({
            'cert_pfx': False,
            'cert_pfx_filename': '',
            'cert_password': '',
        })
        logger.info("🗑️ Certificado reseteado para el endpoint: %s", self.endpoint_url)
        return _notify_success(self.env, '🗑️ Certificado eliminado', _('El certificado ha sido eliminado correctamente.'))

    @api.multi
    def action_test_certificate(self):
        self.ensure_one()

        if not self.cert_pfx or not self.cert_password:
            logger.error("🚫 Prueba de certificado fallida: falta el certificado o la contraseña.")
            return _notify_error(self.env, 'Certificado', _('Falta el certificado o la contraseña.'))

        try:
            cert_data = base64.b64decode(self.cert_pfx)
            pkcs12.load_key_and_certificates(
                cert_data,
                self.cert_password.encode('utf-8'),
                backend=default_backend()
            )
            logger.info("🔓 Certificado válido para el endpoint: %s", self.endpoint_url)
            return _notify_success(self.env, '✅ Certificado válido', _('El certificado ha sido cargado correctamente.'))

        except ValueError as e:
            logger.error("🛑 Error de contraseña o archivo corrupto: %s", e)
            return _notify_error(self.env, 'Certificado', _('Contraseña incorrecta o archivo PFX corrupto.'))

        except Exception as e:
            logger.exception("❗ Error inesperado al cargar el certificado: %s", e)
            return _notify_error(self.env, 'Certificado', _('Error inesperado al cargar el certificado: %s') % e)

    # --------------------------------
    # Helpers de crear/cerrar anomalías (v12: account.invoice)
    # --------------------------------
    def _create_or_keep_anomaly(self, inv, a_type, severity, msg):
        """inv es account.invoice en v12."""
        Anom = self.env['verifactu.anomaly'].sudo()
        existing = Anom.search([
            ('company_id', '=', self.company_id.id),
            ('move_id', '=', inv.id),
            ('anomaly_type', '=', a_type),
            ('resolved', '=', False),
        ], limit=1)
        if existing:
            existing.write({'message': msg, 'detected_at': fields.Datetime.now()})
            return existing

        return Anom.create({
            'company_id': self.company_id.id,
            'move_id': inv.id,
            'anomaly_type': a_type,
            'severity': severity,
            'message': msg,
            'resolved': False,
            'detected_at': fields.Datetime.now(),
        })

    def _resolve_anomaly_if_exists(self, inv, a_type):
        Anom = self.env['verifactu.anomaly'].sudo()
        open_anoms = Anom.search([
            ('company_id', '=', self.company_id.id),
            ('move_id', '=', inv.id),
            ('anomaly_type', '=', a_type),
            ('resolved', '=', False),
        ])
        if open_anoms:
            open_anoms.write({'resolved': True, 'resolved_at': fields.Datetime.now()})

    # --------------------------------
    # Reglas de detección (v12: account.invoice)
    # --------------------------------
    def _check_stale_pending(self):
        """open/paid + pending más de N días → crear/actualizar anomalía; cerrar si se corrige."""
        if not self.anomaly_stale_days:
            return
        limit = fields.Date.to_date(fields.Date.today()) - timedelta(days=int(self.anomaly_stale_days))

        domain = [
            ('type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')),
            ('state', 'in', ('open', 'paid')),        # v12: facturas validadas
            ('date_invoice', '!=', False),
            ('company_id', '=', self.company_id.id),
        ]
        Invoices = self.env['account.invoice'].sudo()
        invoices = Invoices.search(domain, limit=5000)
        for inv in invoices:
            vf_status = getattr(inv, 'verifactu_status', '') or ''
            if vf_status in ('pending',) and inv.date_invoice and inv.date_invoice <= limit:
                name = inv.number or inv.reference or inv.display_name or str(inv.id)
                msg = _("Factura '%(name)s' pendiente más de %(n)s días (fecha: %(d)s).") % {
                    'name': name, 'n': self.anomaly_stale_days, 'd': inv.date_invoice or '-'
                }
                self._create_or_keep_anomaly(inv, 'stale_pending', 'warning', msg)
            else:
                self._resolve_anomaly_if_exists(inv, 'stale_pending')

    def _check_out_of_order(self):
        """Factura pendiente con otra ya enviada de fecha posterior → anomalía (v12)."""
        Inv = self.env['account.invoice'].sudo()
        domain = [
            ('type', 'in', ('out_invoice', 'out_refund')),
            ('state', 'in', ('open', 'paid')),
            ('date_invoice', '!=', False),
            ('company_id', '=', self.company_id.id),
        ]
        to_check = Inv.search(domain, limit=5000)
        for inv in to_check:
            vf_status = getattr(inv, 'verifactu_status', '') or ''
            if vf_status not in ('pending',):
                self._resolve_anomaly_if_exists(inv, 'out_of_order')
                continue

            newer_sent = Inv.search([
                ('id', '!=', inv.id),
                ('type', 'in', ('out_invoice', 'out_refund')),
                ('state', 'in', ('open', 'paid')),
                ('verifactu_status', 'in', ('sent', 'accepted_with_errors')),
                ('date_invoice', '>', inv.date_invoice),
                ('company_id', '=', inv.company_id.id),
            ], limit=1)

            if newer_sent:
                newer_name = newer_sent.number or newer_sent.reference or newer_sent.display_name or str(newer_sent.id)
                msg = _("Existe una factura ya enviada con fecha posterior: %(name)s — %(date)s. "
                        "Revisa el orden cronológico antes de enviar.") % {
                            'name': newer_name,
                            'date': newer_sent.date_invoice or '-'
                        }
                self._create_or_keep_anomaly(inv, 'out_of_order', 'error', msg)
            else:
                self._resolve_anomaly_if_exists(inv, 'out_of_order')

    # --------------------------------
    # Punto de entrada del CRON
    # --------------------------------
    @api.model
    def cron_scan_anomalies(self):
        configs = self.sudo().search([('anomaly_cron_enabled', '=', True)])
        for cfg in configs:
            with self.env.cr.savepoint():
                try:
                    cfg._check_stale_pending()
                    cfg._check_out_of_order()
                except Exception:
                    logger.exception("Error escaneando anomalías (company %s)", cfg.company_id.id)
