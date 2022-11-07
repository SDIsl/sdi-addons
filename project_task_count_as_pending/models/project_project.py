###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _compute_unclosed_task_count(self):
        closed_types = self.env['project.task.type'].search([
            ('pending', '=', True),
        ]).mapped('id')
        for project in self:
            project.unclosed_task_count = len(
                project.task_ids.filtered(
                    lambda l: l.stage_id.id in closed_types
                )
            )

    unclosed_task_count = fields.Integer(
        compute='_compute_unclosed_task_count',
        string='Unclosed Tasks',
    )
