###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    project_task_disable_auto_subscribe = fields.Boolean(
        string='Disable auto subscribe on project task creation',
        help='''Check to disable auto subscription when the user creates a new
                project task.''',
    )
    project_disable_auto_subscribe = fields.Boolean(
        string='Disable auto subscribe on project creation',
        help='''Check to disable auto subscription when the user creates a new
                project.''',
    )
