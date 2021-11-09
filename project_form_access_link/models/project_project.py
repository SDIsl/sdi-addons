###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models


class Project(models.Model):
    _inherit = 'project.project'

    def open_project_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }
