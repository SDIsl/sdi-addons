# verifactu/services/resender.py

from odoo.exceptions import UserError
from odoo import _

class VerifactuResender:
    def __init__(self, invoice):
        self.invoice = invoice

    def resend(self):
        invoice = self.invoice
        invoice.ensure_one()

        endpoint_config = invoice.env["verifactu.endpoint.config"].search([], limit=1)
        if not endpoint_config or not endpoint_config.endpoint_url:
            invoice.message_post(body=_("⚠️ No se ha configurado un endpoint de VeriFactu."))
            return {
                "notification": {
                    "title": "Error",
                    "message": "⚠️ No se ha configurado un endpoint de VeriFactu.",
                    "type": "warning"
                },
                "success": False
            }

        try:
            invoice.generate_verifactu_xml()
            #invoice.message_post(body=_(f"🔄 Factura {invoice.number} reenviada a VeriFactu."))
            return {
                "notification": {
                    "title": "Reenvío exitoso",
                    "message": f"✅ Factura {invoice.number} enviada correctamente a VeriFactu.",
                    "type": "success"
                },
                "success": True
            }

        except Exception as e:
            invoice.message_post(body=_(f"🛑 Error al reenviar factura {invoice.number}: {str(e)}"))
            return {
                "notification": {
                    "title": "Error de reenvío",
                    "message": f"🛑 Error al reenviar factura {invoice.number}: {str(e)}",
                    "type": "danger"
                },
                "success": False
            }
