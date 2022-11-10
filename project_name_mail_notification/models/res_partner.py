###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _notify(self, message, rdata, record, force_send=False,
                send_after_commit=True, model_description=False,
                mail_auto_delete=True):
        change_msg = True
        for type in [user.get('type', '') for user in rdata]:
            if type != 'user' or not record or not record.project_id or \
                    not message.record_name or message.subject:
                change_msg = False
                break
        if change_msg:
            message.subject = 'Re: ( %s ) %s' % (record.project_id.name,
                                                 message.record_name)
        return super()._notify(message, rdata, record, force_send,
                               send_after_commit, model_description,
                               mail_auto_delete)
