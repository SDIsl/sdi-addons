# repo/sdi-addons/sdi_account_payment_return/models/account_payment_return.py

from odoo import models, api


class AccountPaymentReturn(models.Model):
    _inherit = 'payment.return'

    @api.multi
    def notify_return(self):
        template_id = self.env['ir.config_parameter'].sudo().get_param(
            'sdi_account_payment_return.payment_return_mail_template_id'
        )
        if template_id:
            template = self.env['mail.template'].browse(int(template_id))
        else:
            # Busca la plantilla por defecto (ajusta el dominio según tu caso)
            template = self.env.ref(
                'sdi_account_payment_return.mail_template_payment_return_line_notify',
                raise_if_not_found=False)
        all_bodies = []
        for record in self:
            for move in record.line_ids:  # Ajusta este campo según tu modelo
                if template and move.partner_id:
                    mail = template.with_context(
                        default_email_to=move.partner_id.email,
                        object=record
                    ).generate_email(move.id)
                    self.env['mail.mail'].create(mail).send()
                    all_bodies.append(mail.get('body_html', ''))
                    move.partner_id.message_post(
                        body=mail.get('body_html', ''),
                        subject=mail.get('subject', ''),
                        subtype='mail.mt_note'
                    )
        if all_bodies:
            self.message_post(
                body='<hr/>'.join(all_bodies),
                subtype='mail.mt_note'
            )
