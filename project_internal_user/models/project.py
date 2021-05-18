###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    user_id = fields.Many2one(
        domain=[('share', '=', False)],
    )
