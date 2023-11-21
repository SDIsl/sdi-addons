###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ContractTemplate(models.Model):
    _inherit = 'contract.template'

    active = fields.Boolean(
        default=True,
    )
