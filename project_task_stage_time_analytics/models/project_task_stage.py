###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTaskStage(models.Model):
    _inherit = 'project.task.type'

    initial = fields.Boolean(
        string='Initial stage',
        help='This stage is the initial one in the project task cycle.',
    )
    final = fields.Boolean(
        string='Final stage',
        help='This stage is the final one in the project task cycle.',
    )
