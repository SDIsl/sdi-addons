# models/verifactu_requirement_wizard.py

# Desarrollado por Juan Ormaechea (Mr. Rubik) — Todos los derechos reservados
# Este módulo está protegido por la Odoo Proprisetary License v1.0
# Cualquier redistribución está prohibida sin autorización expresa.


from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VerifactuRequirementWizard(models.TransientModel):
    _name = "verifactu.requirement.wizard"
    _description = "Requerimiento para modo No VeriFactu"

    ref_requerimiento = fields.Char(string="Referencia de Requerimiento", required=True)

    def confirm(self):
        active_id = self.env.context.get("active_id")
        move = self.env["account.invoice"].browse(active_id)
        if not self.ref_requerimiento:
            raise UserError(_("Debes indicar el código del requerimiento"))

        # Activamos el modo No VeriFactu en la factura
        move.write({
            "verifactu_is_active": False,
            "verifactu_requerimiento": self.ref_requerimiento,
            "verifactu_generated": False
        })

        # Actualizamos el endpoint requerido para este modo
        config = self.env["verifactu.endpoint.config"].sudo().search([
    ('company_id', '=', self.env.user.company_id.id)
], limit=1)
        config.endpoint_url = ""

        move.message_post(body=_(
            "⚠️ Activado el modo No VeriFactu con requerimiento: %s .Establece de nuevo una url (endoint) de VeriFactu."
        ) % self.ref_requerimiento)
        return {"type": "ir.actions.act_window_close"}

