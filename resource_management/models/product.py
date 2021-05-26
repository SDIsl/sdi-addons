###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_a_resource = fields.Boolean(
        string='Is a resource',
    )
    expiration_date = fields.Date(
        string='Expiration date',
    )
    quantity = fields.Integer(
        string="Quantity",
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
    )
