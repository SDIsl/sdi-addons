###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _write(self, values):
        create_activity = self.env['ir.config_parameter'].get_param(
            'sale_order_no_automatic_upsell_activity.create_upsell_activity'
        )
        if not create_activity:
            self = self.with_context(mail_activity_automation_skip=True)

        return super(SaleOrder, self)._write(values)
