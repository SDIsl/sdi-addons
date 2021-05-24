# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, models

_cancel = logging.getLogger(__name__ + '.cancel')


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.multi
    def action_cancel(self, feedback=False):
        """ Wrapper without feedback because web button add context as
        parameter, therefore setting context to feedback """
        message = self.env['mail.message']
        if feedback:
            self.write(dict(feedback=feedback))
        for activity in self:
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_cancel',
                values={'activity': activity},
                subtype_id=self.env.ref('mail.mt_activities').id,
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.message_ids[0]

        if self.calendar_event_id:
            self.unlink_w_meeting()
        else:
            self.unlink()

        return message.ids and message.ids[0] or False
