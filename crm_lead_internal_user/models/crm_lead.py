###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    user_id = fields.Many2one(
        domain=[('share', '=', False)],
    )
