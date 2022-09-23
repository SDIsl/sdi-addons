###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    @api.multi
    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        for lead in leads:
            for sale_order in lead.order_ids.filtered(
                    lambda s: s.state != 'cancel'):
                sale_order.action_cancel()
        super().action_lost_reason_apply()
