###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    @api.multi
    def action_lost_reason_apply(self):
        self.env['sale.order'].search([
            ('opportunity_id', '=', self.env.user.id),
            ('user_id', '!=', self.env.user.id),
            ('state', '!=', 'cancel')
        ])
        super().action_lost_reason_apply()
