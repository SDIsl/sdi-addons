###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def check_approve(self):
        self.ensure_one()
        if not self.price_subtotal and not [l.id for l in self]:
            self.amount_discount_approve = 0.
            return True
        if self.discount == self.amount_discount_approve:
            self.amount_discount_approve = self.discount
            return True
        if self.discount <= self.env.user.sales_discount_limit:
            self.amount_discount_approve = self.discount
            return True
        return False
