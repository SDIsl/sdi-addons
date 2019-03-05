# -*- coding: utf-8 -*-
# SDI
# © 2012-2015 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    description = fields.Text(string=_("Description"), required=True, Stored=True, )

    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        leads.write({'lost_description': self.description, 'lost_reason': self.lost_reason_id.id})

        return leads.action_set_lost()
