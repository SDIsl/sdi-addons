
###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_closed = fields.Boolean(
        string='Is task closed',
        related='stage_id.closed',
    )
