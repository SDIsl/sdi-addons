# -*- coding: utf-8 -*-
# verifactu/services/qr_content.py

import logging
from io import BytesIO
from datetime import datetime as _dt, date as _date

# Compat URL tools (Py2/Py3)
try:
    # Py3
    from urllib.parse import urlencode, urlparse
except Exception:
    # Py2
    from urllib import urlencode  # noqa
    from urlparse import urlparse  # noqa

import qrcode
from qrcode.constants import ERROR_CORRECT_M
from odoo import fields
from odoo.exceptions import UserError
from odoo.tools.translate import _

from ..utils.verifactu_xml_validator import VerifactuXMLValidator  # limpiar NIF

_logger = logging.getLogger(__name__)

# Compat Py2/Py3
try:
    basestring
except NameError:
    basestring = (str,)


def _as_date(v):
    """Acepta date/datetime/str y devuelve date o None."""
    if not v:
        return None
    if isinstance(v, _date) and not isinstance(v, _dt):
        return v
    if isinstance(v, _dt):
        return v.date()
    if isinstance(v, basestring):
        s = v.strip()
        # intenta YYYY-MM-DD
        try:
            return _dt.strptime(s[:10], "%Y-%m-%d").date()
        except Exception:
            pass
        # intenta DD-MM-YYYY
        try:
            return _dt.strptime(s[:10], "%d-%m-%Y").date()
        except Exception:
            pass
    return None


def _format_ddmmyyyy(v):
    d = _as_date(v)
    return d.strftime("%d-%m-%Y") if d else ""


def _fmt_amount_two(inv, amt):
    """2 decimales (punto). Usa redondeo de la moneda si está disponible."""
    try:
        cur = getattr(inv, 'currency_id', None)
        if cur:
            try:
                amt = cur.round(amt or 0.0)
            except Exception:
                amt = round(amt or 0.0, 2)
        else:
            amt = round(amt or 0.0, 2)
    except Exception:
        amt = round(amt or 0.0, 2)
    return "%.2f" % (amt,)


class VerifactuQRContentGenerator(object):
    def __init__(self, invoice, config, factura_verificable=True):
        self.invoice = invoice
        self.config = config
        self.factura_verificable = factura_verificable

    # ---------- Helpers compat 10–18 ----------
    def _get_invoice_number(self, invoice):
        """Odoo 10–12: number ; Odoo 13+: name."""
        return (getattr(invoice, 'number', None) or
                getattr(invoice, 'name', None) or
                u"")

    def _get_invoice_date(self, invoice):
        """Odoo 10–12: date_invoice ; Odoo 13+: invoice_date ; fallback: date."""
        return (getattr(invoice, 'date_invoice', None) or
                getattr(invoice, 'invoice_date', None) or
                getattr(invoice, 'date', None))

    def _is_test_environment(self):
        """
        Detecta TEST si el host del endpoint contiene 'prewww' (p.ej. prewww2)
        o si no hay endpoint (por seguridad trata como TEST).
        """
        url = (getattr(self.config, 'endpoint_url', u"") or u"").strip()
        try:
            host = urlparse(url).netloc or ""
        except Exception:
            host = ""
        return not url or ('prewww' in (host or ""))

    def _urlencode_utf8(self, params):
        """
        Compat: Py2 no admite 'encoding' en urlencode. Normalizamos a bytes utf-8 en Py2.
        En Py3 dejamos str (unicode).
        """
        try:
            return urlencode(params)  # Py3
        except TypeError:
            enc = {}
            for k, v in params.items():
                if isinstance(k, basestring):
                    k = k.encode('utf-8')
                if isinstance(v, basestring):
                    v = v.encode('utf-8')
                enc[k] = v
            return urlencode(enc)

    # ---------- API pública ----------
    def generate_content(self):
        inv = self.invoice
        inv.ensure_one()

        # Emisor (NIF) desde la compañía
        company = inv.company_id
        company_vat_raw = ((company and company.vat) or u"").strip()
        emisor_nif = VerifactuXMLValidator.clean_nif_es(company_vat_raw) if company_vat_raw else u""
        if not emisor_nif:
            raise UserError(_("La compañía no tiene un NIF configurado. Es obligatorio para generar el QR."))

        num_serie = self._get_invoice_number(inv)
        if not num_serie:
            raise UserError(_("La factura no tiene número asignado."))

        endpoint = getattr(self.config, 'endpoint_url', None)
        if not endpoint:
            _logger.warning("[VeriFactu QR] Endpoint no configurado: se asumirá entorno de PRUEBAS para la URL.")
        # Fecha: si no hay, usa hoy (sin escribir en el registro para evitar side effects)
        fecha_src = self._get_invoice_date(inv)
        if not fecha_src:
            try:
                _logger.warning("[VeriFactu QR] La factura %s no tenía fecha; usando la actual.", (num_serie or "[sin número]"))
            except Exception:
                _logger.warning("[VeriFactu QR] La factura no tenía fecha; usando la actual.")
            fecha_src = fields.Date.context_today(inv)
        fecha = _format_ddmmyyyy(fecha_src)  # <-- DD-MM-YYYY (requerido por AEAT)

        importe = _fmt_amount_two(inv, getattr(inv, 'amount_total', 0.0))

        query = self._urlencode_utf8({
            "nif": emisor_nif,
            "numserie": num_serie,
            "fecha": fecha,
            "importe": importe,
        })

        # Selección de URL oficial (TEST vs PROD) y (Verifactu vs NoVerifactu)
        is_test = self._is_test_environment()
        if self.factura_verificable:
            qr_url_base = (
                "https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQR"
                if is_test else
                "https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQR"
            )
        else:
            qr_url_base = (
                "https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQRNoVerifactu"
                if is_test else
                "https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQRNoVerifactu"
            )

        return u"%s?%s" % (qr_url_base, query)

    def generate_qr_binary(self):
        content = self.generate_content()
        qr = qrcode.QRCode(
            error_correction=ERROR_CORRECT_M,
            box_size=4,
            border=1
        )
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image()

        # Compat: distintas firmas según versión de qrcode/PIL
        try:
            img = qr.make_image(fill_color="black", back_color="white")
        except TypeError:
            try:
                img = qr.make_image(fill="black", back_color="white")
            except TypeError:
                img = qr.make_image()

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
