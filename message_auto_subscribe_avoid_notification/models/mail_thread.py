###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _message_auto_subscribe_followers(
            self, updated_values, default_subtype_ids):
        res = super()._message_auto_subscribe_followers(
            updated_values, default_subtype_ids)
        for pid, sids, template in res:
            res_user = self.env['res.users'].search(
                [('partner_id', '=', pid)], limit=1)
            for model in res_user.model_ids:
                if self._name == model.model:
                    res = [(pid, sids, False)]
        return res
