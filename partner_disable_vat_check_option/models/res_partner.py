###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat', 'country_id')
    def check_vat(self):
        params = self.env['ir.config_parameter'].sudo()
        vat_check_disabled = params.get_param(
            'partner_disable_vat_check_option.disable_vat_check')
        if vat_check_disabled:
            return
        return super().check_vat()
