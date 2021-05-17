###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    user_id = fields.Many2one(
        domain=[('share', '=', False)],
    )
