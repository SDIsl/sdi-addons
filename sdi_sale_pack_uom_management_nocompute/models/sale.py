from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.product_uom = self.product_id.uom_in_sales_id
        return result
