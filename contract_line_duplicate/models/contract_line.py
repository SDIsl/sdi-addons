###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models, _


class ContractLine(models.Model):
    _inherit = 'contract.line'

    def open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Duplicate Contract Line'),
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'duplicate.contract.line.wizard',
            'context': {
                'default_date_start': self.date_start,
                'default_date_end': self.date_end,
                'default_recurring_next_date': self.recurring_next_date,
                'default_discount': self.discount,
                'default_contract_line_id': self.id,
            }
        }
