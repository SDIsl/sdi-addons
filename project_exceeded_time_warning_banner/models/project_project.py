###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _bring_warning_message(self):
        warn_text = self.env['ir.config_parameter'].get_param(
            'project_exceeded_time_warning_banner.warning_message'
            ) or 'Project time balance is negative'

        self.update({
             'warning_message': warn_text
         })

    unit_balance = fields.Float(
        string='Unit Balance',
        related='analytic_account_id.unit_balance'
        )

    show_banner = fields.Boolean(
        string='Show Warning Banner',
        related='type_id.show_banner'
    )

    warning_message = fields.Char(
        string='Warning Message ',
        compute=_bring_warning_message

    )
