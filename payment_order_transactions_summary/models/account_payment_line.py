###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    invoice_date = fields.Date(
        string='Invoice date',
        compute='_compute_date_invoice',
    )

    def _compute_date_invoice(self):
        for line in self:
            if line.move_line_id and line.move_line_id.move_id:
                line.invoice_date = line.move_line_id.move_id.invoice_date
