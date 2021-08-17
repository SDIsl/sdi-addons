from odoo import api, fields, models


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    invoice_date = fields.Date(
        string='Invoice date',
        compute='_compute_date_invoice',
    )

    @api.multi
    def _compute_date_invoice(self):
        for line in self:
            if line.move_line_id and line.move_line_id.invoice_id:
                line.invoice_date = line.move_line_id.invoice_id.date_invoice

