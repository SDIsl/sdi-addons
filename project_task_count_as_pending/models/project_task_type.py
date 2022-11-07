###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    pending = fields.Boolean(
        string='Count as pending task',
        default=True,
    )
