###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    contract_clause = fields.Html(
        string='ANNEX II: Clausules and Conditions',
        help='Terms and conditions of the contract',
    )
    service_level = fields.Html(
        string='ANNEX I: Service Level',
        help='Characteristics and conditions of the level of service offered',
    )
