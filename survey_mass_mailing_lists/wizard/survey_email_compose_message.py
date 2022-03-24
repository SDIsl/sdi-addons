###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class SurveyEmailComposeMessage(models.TransientModel):
    _inherit = 'survey.mail.compose.message'

    mass_mailing_lists_ids = fields.Many2many(
        string='Existing contact lists',
        comodel_name='mail.mass_mailing.list',
    )
    used_mass_mailing_lists_ids = fields.Many2many(
        comodel_name='mail.mass_mailing.list',
        relation="used_lists_survey_mail_compose_message",
        column1="survey_mail_compose_message_id",
        column2="used_list_id",
    )

    @api.onchange('mass_mailing_lists_ids')
    def _onchange_mass_mailing_lists_ids(self):
        multi_email = self.multi_email
        for list in self.mass_mailing_lists_ids:
            if list not in self.used_mass_mailing_lists_ids:
                for contact in list.contact_ids:
                    if contact.partner_id:
                        self.update({
                            'partner_ids': [(4, contact.partner_id.id)],
                        })
                    elif contact.email:
                        multi_email += '\n' + contact.email
                self.update({
                    'multi_email': multi_email,
                })
        self.update({
            'used_mass_mailing_lists_ids': [(
                6, 0, self.mass_mailing_lists_ids.ids)],
        })
