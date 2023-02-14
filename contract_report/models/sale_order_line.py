###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    """external_price_subtotal = fields.Float(
        string='External Price Subtotal',
        compute='_compute_external_price_subtotal',
        compute_sudo=True,
    )"""

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
        """categories_ids = [
            self.env.ref('__export__.product_category_5_bcf34707'),
            self.env.ref('__export__.product_category_7_52012f6a'),
            self.env.ref('__export__.product_category_11_1c86bc2e')
        ]"""
        if self.is_contract and self.recurring_interval:
            return self._recurrence_factor(
                    self.recurring_rule_type,
                    self.recurring_interval,
                )
        else:
            return 1

    """
    @api.multi
    @api.depends('price_subtotal', 'recurring_interval', 'contract_uom_id')
    def _compute_external_price_subtotal(self):
        for line in self:
            line.external_price_subtotal += \
                line.price_subtotal / line.recurrence_factor()
    """
