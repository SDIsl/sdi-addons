###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_download_attachment(self):
        tab_id = []
        for rec in self:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.invoice'),
                ('res_id', '=', rec.id)
            ])
            for attachment in attachments:
                tab_id.append(attachment.id)
        url = '/web/binary/download_document_invoice?tab_id=%s' % tab_id
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
