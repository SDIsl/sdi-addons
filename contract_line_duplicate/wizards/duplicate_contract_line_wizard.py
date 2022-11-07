###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class DuplicateContractLineWizard(models.TransientModel):
    _name = 'duplicate.contract.line.wizard'
    _description = 'Assistant to duplicate contract lines'

    date_start = fields.Date(
        string='Date Start',
        required=True,
    )
    date_end = fields.Date(
        string='Date End',
    )
    recurring_next_date = fields.Date(
        string='Date of Next Invoice',
    )
    discount = fields.Float(
        string='Discount',
    )
    contract_line_id = fields.Many2one(
        comodel_name='contract.line',
        required=True,
    )

    def duplicate(self):
        self.contract_line_id.copy(default={
            'contract_id': self.contract_line_id.contract_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'recurring_next_date': self.recurring_next_date,
            'discount': self.discount,
        })
