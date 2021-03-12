from odoo import api, fields, models


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    transactions_count = fields.Integer(
        string='Number of transactions',
        store=True,
        readonly=True,
        compute='_compute_transactions_count',
    )

    @api.multi
    @api.depends('payment_line_ids')
    def _compute_transactions_count(self):
        for order in self:
            order.transactions_count = len(order.payment_line_ids)
