###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rounding_method = fields.Selection(
        selection=[
            ('round_per_line', 'Round per line'),
            ('round_globally', 'Round globally'),
        ],
        string='Rounding Method',
        config_parameter='pos_rounding_method.rounding_method',
    )
