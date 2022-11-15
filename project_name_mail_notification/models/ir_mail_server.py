###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def build_email(self, email_from, email_to, subject, body, email_cc=None,
                    email_bcc=None, reply_to=False, attachments=None,
                    message_id=None, references=None, object_id=False,
                    subtype='plain', headers=None, body_alternative=None,
                    subtype_alternative='plain'):
        object = object_id.split('-')
        rec_model = object[1]
        if email_to and rec_model in ['project.task', 'project.project']:
            rec_id = object[0]
            record = self.env[rec_model].search([('id', '=', rec_id)])
            if record and subject == 'Re: %s' % (record.name):
                emails = [email.rsplit(' ', 1)[-1][1:-1] for email in email_to]
                emailed_users = self.env['res.users'].search([
                    ('partner_id.email', 'in', emails),
                ])
                if emailed_users:
                    internal_users = emailed_users.filtered(
                        lambda user: user.has_group('base.group_user'))
                    if len(emailed_users.ids) == len(internal_users.ids):
                        subject = 'Re: %s ' % (record.name)
                        if rec_model == 'project.task':
                            subject += '( %s )' % (record.project_id.name)
                        subject += '- %s' % (record.partner_id.name)
        return super().build_email(email_from, email_to, subject, body,
                                   email_cc, email_bcc, reply_to, attachments,
                                   message_id, references, object_id, subtype,
                                   headers, body_alternative,
                                   subtype_alternative)
