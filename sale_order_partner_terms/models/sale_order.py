###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['payment_term_id'] = \
            self.payment_term_id or self.partner_id.property_payment_term_id
        invoice_vals['payment_mode_id'] = \
            self.payment_mode_id or self.partner_id.customer_payment_mode_id
        return invoice_vals
