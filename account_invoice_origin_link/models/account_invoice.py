from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    related_sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Document Link',
    )

    related_contract_id = fields.Many2one(
        comodel_name='contract.contract',
        string='Document Link',
    )
