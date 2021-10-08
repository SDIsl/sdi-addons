###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_secondary_uom_id = fields.Many2one(
        comodel_name='product.secondary.unit',
        string='Default secondary unit for sales',
    )
