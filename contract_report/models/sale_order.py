###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_signature = fields.Datetime(
        string='Date Signature',
    )

    def set_date_signature(self):
        for record in self:
            record.date_signature = fields.datetime.now()
