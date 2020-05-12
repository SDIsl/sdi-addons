###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('phone2', 'country_id', 'company_id')
    def _onchange_phone2_validation(self):
        if self.phone2:
            self.phone2 = self.phone_format(self.phone2)
