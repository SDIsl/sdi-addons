###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTaskLocation(models.Model):
    _name = 'project.task.location'
    _description = 'Project Task Location'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
