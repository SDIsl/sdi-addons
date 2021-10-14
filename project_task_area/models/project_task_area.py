###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTaskArea(models.Model):
    _name = 'project.task.area'
    _description = 'Project Task Area'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
