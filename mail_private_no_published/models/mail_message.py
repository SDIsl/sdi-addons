###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def _notify(
        self,
        record,
        msg_vals,
        force_send=False,
        send_after_commit=True,
        model_description=False,
        mail_auto_delete=True,
    ):
        self_sudo = self.sudo()
        msg_vals = msg_vals if msg_vals else {}
        if self_sudo._context.get('is_private'):
            self.website_published = False
        return super()._notify(
            record,
            msg_vals,
            force_send=force_send,
            send_after_commit=send_after_commit,
            model_description=model_description,
            mail_auto_delete=mail_auto_delete,
        )

    @api.constrains('is_private')
    def _check_archive(self):
        if self.is_private:
            self.website_published = False

    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            if rec.subtype_id == self.env.ref('mail.mt_note'):
                rec.website_published = False
        return res
