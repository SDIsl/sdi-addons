from lxml import etree
import base64
from odoo.exceptions import UserError
from ..services.logger import VerifactuLogger
from ..utils.cert_handler import VerifactuCertHandler

NS = {
    "sum": "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroLR.xsd",
    "sum1": "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroInformacion.xsd",
}

class VerifactuIntegrityVerifier:
    def __init__(self, invoice, config):
        self.invoice = invoice
        self.config = config

    def _log_error(self, message):
        self.invoice.message_post(body=message)

    def _load_signed_xml(self):
        attachment = self.invoice.env["ir.attachment"].search([
            ("res_model", "=", "account.invoice"),
            ("res_id", "=", self.invoice.id),
            ("name", "ilike", ".xml"),
            ("mimetype", "=", "application/xml"),
        ], limit=1)

        if not attachment:
            self._log_error("🛑 No se ha encontrado el XML firmado de la factura.")
            return None
        return base64.b64decode(attachment.datas)

    def _get_text(self, tree, xpath):
        result = tree.xpath(xpath, namespaces=NS)
        return result[0].text.strip() if result and result[0].text else ""

    def _verify_invoice_fields(self, xml_bytes):
        # ✅ Emisor esperado = company_id (empresa o autónomo), NO el certificado
        inv = self.invoice
        company = inv.company_id

        # Imports locales para evitar dependencias en el módulo entero
        from odoo import fields
        from lxml import etree as LET
        from datetime import datetime, timedelta,clean_nif_es
        from ..utils.verifactu_xml_validator import VerifactuXMLValidator

        # VAT esperado (normalizado)
        expected_vat = ""
        if company.vat:
            expected_vat = VerifactuXMLValidator.clean_nif_es((company.vat or "").strip())

        expected_emisor_name = (company.name or "").strip()
        expected_total = f"{inv.amount_total:.2f}"
        expected_tax = f"{inv.amount_tax:.2f}"

        # Fecha esperada (v13+: invoice_date ; v11/v12: date_invoice ; puede ser str o datetime)
        inv_date = getattr(inv, 'invoice_date', None) or getattr(inv, 'date_invoice', None)
        if isinstance(inv_date, str):
            try:
                inv_date = fields.Date.from_string(inv_date)
            except Exception:
                inv_date = None
        elif isinstance(inv_date, datetime):
            inv_date = inv_date.date()
        expected_date = inv_date.strftime("%d-%m-%Y") if inv_date else ""

        # Número esperado (v13+: name ; v11/v12: number)
        expected_number = (getattr(inv, 'name', None) or getattr(inv, 'number', None) or "").strip()

        # Parse XML
        try:
            tree = LET.fromstring(xml_bytes)
        except Exception as e:
            self._log_error(f"🛑 Error al parsear el XML: {e}")
            return False

        errors = []

        # Campos del nodo IDFactura
        xml_vat         = self._get_text(tree, "//sum1:IDFactura/sum1:IDEmisorFactura")
        xml_total       = self._get_text(tree, "//sum1:ImporteTotal")
        xml_tax         = self._get_text(tree, "//sum1:CuotaTotal")
        xml_date        = self._get_text(tree, "//sum1:IDFactura/sum1:FechaExpedicionFactura")
        xml_number      = self._get_text(tree, "//sum1:IDFactura/sum1:NumSerieFactura")
        xml_emisor_name = self._get_text(tree, "//sum1:NombreRazonEmisor")

        norm = lambda s: (s or "").strip()

        if norm(xml_vat) != norm(expected_vat):
            errors.append(f"NIF incorrecto: XML={xml_vat}, Esperado={expected_vat}")
        if norm(xml_total) != norm(expected_total):
            errors.append(f"Total incorrecto: XML={xml_total}, Esperado={expected_total}")
        if norm(xml_tax) != norm(expected_tax):
            errors.append(f"IVA incorrecto: XML={xml_tax}, Esperado={expected_tax}")
        if norm(xml_date) != norm(expected_date):
            errors.append(f"Fecha incorrecta: XML={xml_date}, Esperado={expected_date}")
        if norm(xml_number) != norm(expected_number):
            errors.append(f"Número incorrecto: XML={xml_number}, Esperado={expected_number}")
        if norm(xml_emisor_name) != norm(expected_emisor_name):
            errors.append(f"Nombre emisor incorrecto: XML={xml_emisor_name}, Esperado={expected_emisor_name}")

        if errors:
            self._log_error("🛑 Errores de integridad:\n" + "\n".join(errors))
            return False

        return True


    def verify(self):
        self.invoice.ensure_one()

        xml = self._load_signed_xml()
        if not xml:
            return False

        if not self._verify_invoice_fields(xml):
            return False

        msg = "✅ Integridad verificada: el contenido del XML coincide con la factura."
        VerifactuLogger(self.invoice).log(msg)
        self.invoice.message_post(body=msg)
        return True
