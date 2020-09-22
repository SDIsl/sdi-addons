###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    contract_sign = fields.Binary(
        string='Contract Sign',
        attachment=True,
        )
    sale_order_process_info = fields.Html(
        string='Sale Order Process',
        help='Steps for the client to make the payment of the service contract.',
    )
