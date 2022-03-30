from odoo import models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _notify(self, message, rdata, record, force_send=False,
                send_after_commit=True, model_description=False,
                mail_auto_delete=True):
        projectpick = self.env['project.task'].search(
            [('name', 'ilike', message.record_name)])
        if projectpick:
            message.subject = message.subject or (
                message.record_name and 'Re: [%s] %s' % (
                    projectpick.project_id.name, message.record_name
                )
            )
        else:
            message.subject = message.subject or (
                message.record_name and 'Re: %s' % message.record_name
            )

        return super()._notify(message, rdata, record, force_send,
                               send_after_commit, model_description,
                               mail_auto_delete
                               )
