###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models, _


class DmsDirectory(models.Model):
    _inherit = 'dms.directory'

    related_lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Related Lead Id',
    )

    def related_lead_link(self):
        return {
            'res_model': 'crm.lead',
            'res_id': self.related_lead_id.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('crm.crm_lead_view_form').id,
            'target': 'self',
        }

    def unlink(self):
        if self.related_lead_id:
            self.related_lead_id.message_post(
                body=_('Directory related has been eliminated')
                )
        return super().unlink()
