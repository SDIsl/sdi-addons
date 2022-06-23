
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    unit_balance = fields.Float(
        string='Unit Balance',
        related='project_id.analytic_account_id.unit_balance'
        )

    showBanner = fields.Boolean(
        string='Show Warning Banner',
        related='project_id.type_id.showBanner'
    )

    warningMessage = fields.Char(
        string='Warning Message',
        related='project_id.warningMessage'
        )
