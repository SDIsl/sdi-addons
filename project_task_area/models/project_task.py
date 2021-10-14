###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'
    area_id = fields.Many2one(
        comodel_name='project.task.area',
        string='Area'
    )
