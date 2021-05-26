###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    resource_ids = fields.One2many(
        comodel_name='product.template',
        inverse_name='employee_id',
        string='Resources',
    )
