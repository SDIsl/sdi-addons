# verifactu/models/_qr_url_mixin.py  (nuevo archivo)
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo import release

class VerifactuQRUrlMixin(models.AbstractModel):
    _name = "verifactu.qr.url.mixin"
    _description = "Mixin para almacenar URL de QR VeriFactu"

    # Campo que verás en la vista
    verifactu_qr_url = fields.Char(string="VeriFactu QR URL", readonly=True, copy=False)

    def _vf_resolve_config(self, company_id):
        return self.env["verifactu.endpoint.config"].sudo().search([("company_id", "=", company_id)], limit=1)

    def _vf_is_noverifactu(self, inv):
        """
        Determina si la factura es 'No VeriFactu'. Ajusta a tu lógica real si tienes un campo específico.
        Por defecto: factura verificable (False => usar URL VeriFactu normal).
        """
        return bool(getattr(inv, "verifactu_noverifactu", False))

    def _vf_generate_and_store_qr_url(self):
        """Genera la URL del QR y la guarda en el campo verifactu_qr_url. No rompe el flujo si falla."""
        # Import aquí para evitar dependencias duras en arranque
        from ..verifactu.services.qr_content import VerifactuQRContentGenerator

        for inv in self:
            try:
                config = self._vf_resolve_config(inv.company_id.id)
                if not config:
                    # No bloquear: limpia campo si procede y sigue
                    inv.sudo().write({"verifactu_qr_url": False})
                    continue

                factura_verificable = not self._vf_is_noverifactu(inv)
                gen = VerifactuQRContentGenerator(inv, config, factura_verificable=factura_verificable)
                url = gen.generate_content()  # solo URL, no imagen
                inv.sudo().write({"verifactu_qr_url": url})
            except Exception:
                # Seguridad: no bloquees ciclo de vida de factura por el QR.
                inv.sudo().write({"verifactu_qr_url": False})
                # Si quieres log, usa tu logger:
                # from ..verifactu.services.logger import VerifactuLogger
                # VerifactuLogger(inv).log("No se pudo generar la URL de QR para esta factura.", level="warning")
                continue


# Parches por versión (v13+ = account.move / v11 = account.invoice)
if release.version_info[0] >= 13:
    class AccountMove_VerifactuQR(models.Model):
        _inherit = ["account.move", "verifactu.qr.url.mixin"]
        _name = "account.move"

        def action_post(self):
            res = super(AccountMove_VerifactuQR, self).action_post()
            try:
                self._vf_generate_and_store_qr_url()
            except Exception:
                pass
            return res
else:
    class AccountInvoice_VerifactuQR(models.Model):
        _inherit = ["account.invoice", "verifactu.qr.url.mixin"]
        _name = "account.invoice"

        def action_invoice_open(self):
            res = super(AccountInvoice_VerifactuQR, self).action_invoice_open()
            try:
                self._vf_generate_and_store_qr_url()
            except Exception:
                pass
            return res
