from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['related_sale_id'] = self.id
        return res
