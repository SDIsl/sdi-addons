###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models
import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cancelation_date_real = fields.Date(
        string='Cancelation Date',
        copy=False,
    )

    def action_cancel(self):
        res = super().action_cancel()
        for rec in self:
            rec.cancelation_date_real = datetime.date.today()
        return res

    def action_draft(self):
        res = super().action_draft()
        for rec in self:
            rec.cancelation_date_real = False
        return res
