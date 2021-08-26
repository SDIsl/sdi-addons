###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class SurveyMailComposeMessage(models.Model):
    _inherit = 'survey.mail.compose.message'

    mass_mailing_lists_ids = fields.Many2many(
        string='Existing contacts',
        comodel_name='mail.mass_mailing.list',
    )
