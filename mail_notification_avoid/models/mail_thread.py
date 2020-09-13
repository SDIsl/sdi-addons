###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _message_notification_recipients(self, message, recipients):
        if not message.author_id.user_ids:
            recipients = recipients.filtered(lambda partner: partner.user_ids)
        return super()._message_notification_recipients(message, recipients)
