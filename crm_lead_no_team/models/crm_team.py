###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.model
    def action_your_pipeline(self):
        res = super().action_your_pipeline()
        res["context"].pop('default_team_id')
        return res
