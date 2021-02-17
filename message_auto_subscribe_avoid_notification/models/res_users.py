###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    unsuscribe_model_ids = fields.Many2many(
        string='Models',
        comodel_name='ir.model',
        help='Select the models in which you do not want to be notified when \
        they assign you to it.',
    )
