###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models
import threading


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def _tracking_headers_add(self, tracking_email_id, headers):
        config_parameter = self.env['ir.config_parameter'].sudo()
        headers = super()._tracking_headers_add(tracking_email_id, headers)
        headers['X-Odoo-{name}-ID'.format(
            name=config_parameter.get_param('mail_tracking_key', 'Tracking')
        )] = headers.pop('X-Odoo-Tracking-ID')
        return headers

    def _tracking_email_get(self, message):
        config_parameter = self.env['ir.config_parameter'].sudo()
        tracking_email_id = False
        tracking_key = 'X-Odoo-{name}-ID'.format(
            name=config_parameter.get_param('mail_tracking_key', 'Tracking'))
        if message.get(tracking_key).isdigit():
            tracking_email_id = int(message[tracking_key])
        return self.env['mail.tracking.email'].browse(tracking_email_id)
