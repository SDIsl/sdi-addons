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
        if res:
            res_user = self.env['res.users'].search(
                [('partner_id', '=', res[0][0])], limit=1)
            for model in res_user.unsuscribe_model_ids:
                if self._name == model.model:
                    res = [(res[0][0], res[0][1], False)]
        return res
