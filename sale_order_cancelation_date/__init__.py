###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from . import models

from odoo import api, SUPERUSER_ID
import datetime


def auto_complete_cancelation_date(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for sale in env['sale.order'].search([('state', '=', 'cancel')]):
        msg = sale.message_ids.filtered(
            lambda m: m.tracking_value_ids.filtered(
                lambda t: t.field == 'state'
                and t.new_value_char == 'Cancelado'
            ))[:1]
        if msg:
            sale.write({
                'cancelation_date_real': msg.date.date()
            })
