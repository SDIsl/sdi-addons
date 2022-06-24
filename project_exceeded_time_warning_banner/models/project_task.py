
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    unit_balance = fields.Float(
        string='Unit Balance',
        related='project_id.analytic_account_id.unit_balance'
        )

    show_banner = fields.Boolean(
        string='Show Warning Banner',
        related='project_id.type_id.show_banner'
    )

    warning_message = fields.Char(
        string='Warning Message',
        related='project_id.warning_message'
        )
