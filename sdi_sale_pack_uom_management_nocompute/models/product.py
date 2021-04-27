from datetime import datetime
from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_default_uom_id(self):
        return self.env["product.uom"].search([], limit=1, order='id').id

    uom_in_sales_id = fields.Many2one(comodel_name='product.uom',
                                      default=_get_default_uom_id,
                                      required=True,
                                      string='UOM by default in sales')
