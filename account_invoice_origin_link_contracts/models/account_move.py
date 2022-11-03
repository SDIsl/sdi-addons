###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    related_contract_id = fields.Many2one(
        comodel_name='contract.contract',
        string='Document Link',
    )
