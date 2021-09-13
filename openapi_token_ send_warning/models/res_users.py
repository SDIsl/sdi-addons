from odoo import _, api, fields, models

import logging
_log = logging.getLogger('Token Send Warining')


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_openapi_mail_receiver = fields.Boolean(
        help='If checked, the user will receive emails from the OpenAPI.',
        string='OpenAPI Mail receiver',
    )

    @api.constrains('openapi_token')
    def _check_openapi_token(self):
        def _send_mail(msg, recipients):
            self.env['mail.mail'].create({
                'body_html': msg,
                'subject': 'OpenAPI token error',
                'email_from': self.env.user.email,
                'recipient_ids': [(6, 0, recipients)],
            }).send()
        for r in self:
            if not self.openapi_token:
                return
            user_ids = self.env['res.users'].search([
                ('is_openapi_mail_receiver', '=', True)])
            recipients = [x.partner_id.id for x in user_ids]
            if not recipients:
                _log.info('No recipients found')
                return
            msg = _(
                '<p>The OpenAPI Token, for the user %s, has changed. '
                'The new one is %s</p>'
            ) % (
                r.name,
                r.openapi_token,
            )
            _send_mail(msg, recipients)
