# -*- coding: utf-8 -*-
# SDI
# © 2012-2015 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, modules


class Users(models.Model):
    _inherit = ['res.users']

    @api.model
    def activity_user_count(self):
        crm_lead_index = -1
        index = 0
        result = super(Users,self).activity_user_count()
        while crm_lead_index < 0 and index < len(result):
            item = result[index]
            if item['model'] == 'crm.lead':
                crm_lead_index = index
            else:
                if item['model'] == 'res.partner':
                    item['icon'] = '/separate_leads_opportunities/static/description/contacts.png'
                index += 1

        if not crm_lead_index < 0:
            result.remove(result[crm_lead_index])

        aux = (self._activity_from_crm_lead_user_count()) + result
        return aux



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
                            act.res_model = 'crm.lead'
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
        self.env.cr.execute(query, (self.env.uid, self.env.uid, self.env.user.partner_id.id))
        activity_from_crm_lead_data = self.env.cr.dictfetchall()

        view_id_lead_form = self.env.ref('crm.crm_case_form_view_leads').id
        view_id_lead_kanban = self.env.ref('crm.view_crm_lead_kanban').id
        # view_id_lead_search = self.env.ref('sdi_crm.view_crm_case_leads_filter').id
        view_id_lead_search = self.env.ref('crm.view_crm_case_leads_filter').id
        # view_id_oppor_form = self.env.ref('sdi_crm.crm_case_form_view_oppor').id
        view_id_oppor_form = self.env.ref('crm.crm_case_form_view_oppor').id
        # view_id_oppor_kanban = self.env.ref('sdi_crm.crm_case_kanban_view_leads').id
        view_id_oppor_kanban = self.env.ref('crm.crm_case_kanban_view_leads').id
        view_id_oppor_search = self.env.ref('crm.view_crm_case_opportunities_filter').id

        is_admin = self.env.user.has_group('sales_team.group_sale_manager')

        user_activities = {}
        for activity in activity_from_crm_lead_data:
            if not user_activities.get(activity['model']):
                user_activities[activity['model']] = {
                    'name': activity['model'],
                    'model': 'crm.lead',
                    'view_id': 138,
                    'total_count': 0, 'today_count': 0, 'overdue_count': 0, 'planned_count': 0,
                }
                if activity['model']== 'lead':
                    user_activities[activity['model']]['icon'] = modules.module.get_module_icon(
                        self.env['crm.lead']._original_module)
                    user_activities[activity['model']]['form_id'] = view_id_lead_form
                    user_activities[activity['model']]['kanban_id'] = view_id_lead_kanban
                    user_activities[activity['model']]['search_id'] = view_id_lead_search
                else:
                    user_activities[activity['model']]['icon'] = '/separate_leads_opportunities/static/description/opportunity_icon.png'
                    user_activities[activity['model']]['form_id'] = view_id_oppor_form
                    user_activities[activity['model']]['kanban_id'] = view_id_oppor_kanban
                    user_activities[activity['model']]['search_id'] = view_id_oppor_search

                user_activities[activity['model']]['is_admin'] = is_admin
            user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
            if activity['states'] in ('today','overdue'):
                user_activities[activity['model']]['total_count'] += activity['count']

        return list(user_activities.values())
