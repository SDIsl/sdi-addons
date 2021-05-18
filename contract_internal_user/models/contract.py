###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    user_id = fields.Many2one(
        domain=[('share', '=', False)],
    )
