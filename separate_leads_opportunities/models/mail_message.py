# -*- coding: utf-8 -*-
# SDI
# © 2012-2015 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, api, _


class Message(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def message_format(self):
        """
        Distinguish from the snack icon between initiatives and opportunities to:
         - to put different icons
         - Redirect to the appropriate form view.
        """
        message_values =super(Message,self).message_format()
        view_id_lead_form = self.env.ref('crm.crm_case_form_view_leads').id
        view_id_oppor_form = self.env.ref('crm.crm_case_form_view_oppor').id
        for m in message_values:
            if m['model']== 'crm.lead':
                id = m['res_id']
                lead = self.env['crm.lead'].browse(id)
                m['type'] = lead.type
                if lead.type == 'opportunity':
                    m['module_icon'] = '/separate_leads_opportunities/static/description/opportunity_icon.png'
                    m['form_id'] = view_id_oppor_form
                else:
                    m['form_id'] = view_id_lead_form
            else:
                m['form_id'] = False
        return message_values

