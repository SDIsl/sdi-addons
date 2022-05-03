###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.constrains('user_id')
    @api.multi
    def _valid_team(self):
        pass
