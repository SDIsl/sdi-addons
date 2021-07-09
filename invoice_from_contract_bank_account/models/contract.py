# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contract(models.Model):
    _inherit = "contract.contract"

    @api.model
    def _finalize_invoice_creation(self, invoices):
        res = super(Contract, self)._finalize_invoice_creation(
            invoices)
        for invoice in invoices.filtered(
                lambda x: x.payment_mode_id and x.payment_mode_id.facturae_code == '04'):
            invoice.partner_bank_id = invoice.payment_mode_id.fixed_journal_id.bank_account_id or False
        return res

