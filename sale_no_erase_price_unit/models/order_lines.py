# Copyright 2019 SDi Soluciones
# Oscar Soto - <osoto@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.price_unit or self.price_unit == 0:
            super().product_uom_change()
