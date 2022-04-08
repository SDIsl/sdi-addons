###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    internal_notes = fields.Html(
        string='Internal Notes',
        help='Internal notes about order',
    )
