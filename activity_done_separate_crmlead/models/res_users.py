# -*- coding: utf-8 -*-
# SDI
# © 2012-2015 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models, modules

class Users(models.Model):
    _inherit = ['res.users']

    @api.model
    def activity_user_count(self):
        query = """SELECT m.id, count(*), act.res_model as model,
                CASE
                    WHEN now()::date - act.date_deadline::date = 0 Then 'today'
                    WHEN now()::date - act.date_deadline::date > 0 Then 'overdue'
                    WHEN now()::date - act.date_deadline::date < 0 Then 'planned'
                END AS states
            FROM mail_activity AS act
            JOIN ir_model AS m ON act.res_model_id = m.id

            WHERE                                         
                 act.active = true
                 and act.res_model <> 'crm.lead'
                 and (
                            act.user_id = %s
                            or
                            (
                                act.user_id <> %s
                                and
                                act.calendar_event_id in (
                                    select event_id from calendar_attendee as att
                                    where att.partner_id = %s
                                    )
                            )
                        )
            GROUP BY m.id, states, act.res_model;
            """
        self.env.cr.execute(query, (self.env.uid,
                                    self.env.uid,
                                    self.env.user.partner_id.id))
        activity_data = self.env.cr.dictfetchall()
        model_ids = [a['id'] for a in activity_data]
        model_names = {n[0]: n[1] for n in self.env['ir.model'].browse(
            model_ids).name_get()}

        user_acts = {}
        for act in activity_data:
            if not user_acts.get(act['model']):
                user_acts[act['model']] = {
                    'name': model_names[act['id']],
                    'model': act['model'],
                    'icon': modules.module.get_module_icon(
                        self.env[act['model']]._original_module),
                    'total_count': 0,
                    'today_count': 0,
                    'overdue_count': 0,
                    'planned_count': 0,
                }
                if act['model'] == 'res.partner':
                    user_acts[act['model']]['icon'] = '/separate_leads_opportunities/static/description/contacts.png'
            user_acts[act['model']]['%s_count' % act['states']] += act['count']
            if act['states'] in ('today', 'overdue'):
                user_acts[act['model']]['total_count'] += act['count']
        aux = (self._activity_from_crm_lead_user_count())

        return aux + list(user_acts.values())

    def _activity_from_crm_lead_user_count(self):
        query = """SELECT m.id, count(*), l.type as model,
                CASE
                    WHEN now()::date - act.date_deadline::date = 0 Then 'today'
                    WHEN now()::date - act.date_deadline::date > 0 Then 'overdue'
                    WHEN now()::date - act.date_deadline::date < 0 Then 'planned'
                END AS states
            FROM mail_activity AS act
            join crm_lead AS l on l.id = act.res_id
            JOIN ir_model AS m ON act.res_model_id = m.id                 

            WHERE
                    act.active = true
                    and act.res_model = 'crm.lead'
                    and (
                            act.user_id = %s
                            or
                            (
                                act.user_id <> %s
                                and
                                act.calendar_event_id in (
                                    select event_id from calendar_attendee as att
                                    where att.partner_id = %s
                                    )
                            )
                        )
            GROUP by l.type, m.id, states, act.res_model;        
        """
        self.env.cr.execute(query, (self.env.uid,
                                    self.env.uid,
                                    self.env.user.partner_id.id))
        activity_from_crm_lead_data = self.env.cr.dictfetchall()

        view_id_lead_form = self.env.ref('crm.crm_case_form_view_leads').id
        view_id_lead_kanban = self.env.ref('crm.view_crm_lead_kanban').id
        view_id_lead_search = self.env.ref(
            'crm.view_crm_case_leads_filter').id
        view_id_oppor_form = self.env.ref('crm.crm_case_form_view_oppor').id
        view_id_oppor_kanban = self.env.ref(
            'crm.crm_case_kanban_view_leads').id
        view_id_oppor_search = self.env.ref(
            'crm.view_crm_case_opportunities_filter').id

        is_admin = self.env.user.has_group('sales_team.group_sale_manager')

        user_acts = {}
        for act in activity_from_crm_lead_data:
            if not user_acts.get(act['model']):
                user_acts[act['model']] = {
                    'name': act['model'],
                    'model': 'crm.lead',
                    'view_id': 138,
                    'total_count': 0,
                    'today_count': 0,
                    'overdue_count': 0,
                    'planned_count': 0,
                }
                model= act['model']
                if model == 'lead':
                    user_acts[model]['icon'] = modules.module\
                        .get_module_icon(self.env['crm.lead']._original_module)
                    user_acts[model]['form_id'] = view_id_lead_form
                    user_acts[model]['kanban_id'] = view_id_lead_kanban
                    user_acts[model]['search_id'] = view_id_lead_search
                else:
                    user_acts[model]['icon'] = '/separate_leads_opportunities/static/description/opportunity_icon.png'
                    user_acts[model]['form_id'] = view_id_oppor_form
                    user_acts[model]['kanban_id'] = view_id_oppor_kanban
                    user_acts[model]['search_id'] = view_id_oppor_search

                user_acts[model]['is_admin'] = is_admin
            user_acts[model]['%s_count' % act['states']] += act['count']
            if act['states'] in ('today','overdue'):
                user_acts[model]['total_count'] += act['count']

        return list(user_acts.values())
