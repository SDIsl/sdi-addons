###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    external_price_unit = fields.Float(
        string='External Price Unit',
        compute='_compute_external_price_unit',
        compute_sudo=True,
    )

    def _recurrence_factor(self, type, recurrence):
        map = {
            'daily': 365,
            'weekly': 365 / 7,
            'monthly': 12,
            'monthlylastday': 12,
            'quarterly': 4,
            'semesterly': 2,
            'yearly': 1,
        }
        return map.get(type, 0) / recurrence

    def recurrence_factor(self):
        self.ensure_one()
        if self.is_contract and self.recurring_interval:
            return self._recurrence_factor(
                    self.recurring_rule_type,
                    self.recurring_interval,
                )
        else:
            return 1

    @api.multi
    @api.depends('price_unit', 'recurring_interval', 'recurring_rule_type')
    def _compute_external_price_unit(self):
        for line in self:
            line.external_price_unit += \
                line.price_unit / line.recurrence_factor()
