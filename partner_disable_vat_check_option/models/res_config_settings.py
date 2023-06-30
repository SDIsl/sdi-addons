###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_vat_check = fields.Boolean(
        string='Deshabilitar la comprobación de NIF',
        readonly=False,
    )
