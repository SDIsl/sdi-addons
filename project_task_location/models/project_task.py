###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    location_id = fields.Many2one(
        comodel_name='project.task.location',
        string='Location',
        track_visibility='onchange',
        ondelete='restrict',
    )
