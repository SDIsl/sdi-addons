###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    classification_id = fields.Many2one(
        comodel_name='project.classification',
        string='Classification',
    )
