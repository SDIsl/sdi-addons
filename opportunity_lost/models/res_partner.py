# -*- coding: utf-8 -*-
# SDI
# © 2012-2015 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools, _


class Partner(models.Model):
    _inherit = 'res.partner'

    # Add some attribute
    opportunity_count_lost = fields.Integer("Opportunity lost", compute='_compute_opportunity_lost_count')

    @api.multi
    def _compute_opportunity_lost_count(self):
        """
        Calculate the number of missed opportunities.
        """
        for partner in self:
            # the opportunity count should counts the opportunities of this company and all its contacts
            operator = 'child_of' if partner.is_company else '='
            partner.opportunity_count_lost = self.env['crm.lead'].search_count(
                [('partner_id', operator, partner.id),
                 ('type', '=', 'opportunity'),
                 ('active', '=', False),
                 ('probability','=','0')])
            if partner.is_company:
                workers = self.env['res.partner'].search([('parent_id', '=', partner.id)])
                for w in workers:
                    partner.meeting_count += len(w.meeting_ids)
