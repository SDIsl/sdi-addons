###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_signature = fields.Datetime(
        string='Date Signature',
    )

    def set_date_signature(self):
        for record in self:
            record.date_signature = fields.datetime.now()

    def annual_untaxed_amount_subtotal(self, qty, from_unit):
        to_unit = self.env.ref('contract_sale_uom.uom_annual')
        if not from_unit or not qty:
            return qty
        if from_unit == to_unit:
            amount = qty
        else:
            amount = qty * from_unit.factor * to_unit.factor_inv
        return amount
