###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_ordered_qty = fields.Integer(
        string='Total ordered qty',
        compute='_compute_total_storable_qty',
    )
    total_delivered_qty = fields.Integer(
        string='Total delivered qty',
        compute='_compute_total_storable_qty',
    )
    total_invoiced_qty = fields.Integer(
        string='Total invoiced qty',
        compute='_compute_total_storable_qty',
    )

    @api.depends(
        'order_line.product_uom_qty',
        'order_line.qty_delivered',
        'order_line.qty_invoiced',
    )
    def _compute_total_storable_qty(self):
        for order in self:
            total_ordered_qty = 0
            total_delivered_qty = 0
            total_invoiced_qty = 0
            for line in order.order_line.filtered(
                    lambda o: o.product_type == 'product'):
                total_ordered_qty += line.product_uom_qty
                total_delivered_qty += line.qty_delivered
                total_invoiced_qty += line.qty_invoiced
            order.update({
                'total_ordered_qty': total_ordered_qty,
                'total_delivered_qty': total_delivered_qty,
                'total_invoiced_qty': total_invoiced_qty,
            })
