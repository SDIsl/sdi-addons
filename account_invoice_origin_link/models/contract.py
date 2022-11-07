###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    @api.multi
    def _prepare_invoice(self, date_invoice, journal=None):
        vals = super()._prepare_invoice(date_invoice, journal)
        vals['related_contract_id'] = self.id
        return vals
