###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTaskStreet(models.Model):
    _name = 'project.task.street'
    _description = 'Project Task Street'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
