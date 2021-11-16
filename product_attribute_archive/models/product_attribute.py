###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    active = fields.Boolean(
        default=True,
    )
