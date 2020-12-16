###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def action_cancel(self):
        message = self.env['mail.message']
        for activity in self:
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail_activity_cancel.message_activity_cancel',
                values={'activity': activity},
                subtype_id=self.env.ref('mail.mt_activities').id,
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.message_ids[0]
        self.unlink()
        return message.ids and message.ids[0] or False
