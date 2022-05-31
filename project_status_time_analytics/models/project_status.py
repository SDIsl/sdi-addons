###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectStatus(models.Model):
    _inherit = 'project.status'

    initial = fields.Boolean(
        string='Initial status',
        help='This status is the initial one in the project cycle.',
    )
    final = fields.Boolean(
        string='Final status',
        help='This status is the final one in the project cycle.',
    )
