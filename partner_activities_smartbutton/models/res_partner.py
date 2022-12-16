###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    activities_count = fields.Integer(
        compute='_compute_activities_count',
        string='Activities Count',
    )

    def _compute_activities_count(self):
        model = self.env['mail.activity']
        for partner in self:
            partner.activities_count = model.search_count([
                ('partner_id', 'child_of', partner.commercial_partner_id.id),
                ('state', 'not in', ['done'])
            ])
