# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import datetime
from odoo import api, models, fields, _
from odoo.tools.safe_eval import safe_eval

_unlink = logging.getLogger(__name__ + '.unlink')
_done = logging.getLogger(__name__ + '.done')


class MailActivity(models.Model):
    _inherit = "mail.activity"

    active = fields.Boolean(default=True)
    done_date = fields.Datetime('Done Date',
                                search='_search_activity_done_date',
                                default=None)

    def action_feedback(self, feedback=False):
        events = self.mapped('calendar_event_id')
        message = self.env['mail.message']
        if feedback:
            self.write(dict(feedback=feedback))
        for activity in self:
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={'activity': activity},
                subtype_id=self.env.ref('mail.mt_activities').id,
                mail_activity_type_id=activity.activity_type_id.id,
            )
            message |= record.message_ids[0]

        if feedback:
            for event in events:
                description = event.description
                description = \
                    '%s\n%s%s' % (description or '', _("Feedback: "), feedback)
                event.write({'description': description})

        self.done()
        return message.ids and message.ids[0] or False

    @api.multi
    def done(self):
        """
        When we mark an activity as done, it isn't erased
        now put the property 'active' to 'False'.
        :return: action
        """
        self._check_access('unlink')
        for act in self:
            if act.date_deadline <= fields.Date.today():
                self.env['bus.bus'].sendone(
                    (self._cr.dbname, 'res.partner',
                     act.user_id.partner_id.id),
                    {'type': 'activity_updated', 'activity_deleted': True})
            act.active = False
            act.done_date = datetime.datetime.utcnow()
            if act.calendar_event_id:
                act.calendar_event_id.active = False

        self.modified(self._fields)
        self._check_concurrency()

        self.invalidate_cache()
        self.recompute()
        _done.info('User #%s mark done %s activity with IDs: %r',
                   self._uid, self._name, self.ids)
        return True

    def unlink_w_meeting(self):
        model = self.res_model
        res_id = self.res_id
        res = super(MailActivity, self).unlink_w_meeting()
        self.invalidate_cache()
        self.recompute()
        self.env[model].browse(res_id)._compute_meeting_count()
        return res

    @api.model
    def _search_activity_done_date(self, operator, operand):
        '''
        Filter.
        Hay que probarlo.
        :param operator:
        :param operand:
        :return:
        '''
        return [('done_date', operator, fields.Datetime.from_string(operand))]

    @api.constrains('active')
    def onchange_active(self):
        """
        Si cambia el estado de una actividad-reunión a FALSE que se actualizen
        los contadores.
        :return:
        """
        self.env[self.res_model].browse(self.res_id)._compute_meeting_count()

    @api.model
    def action_your_activities(self):
        view_kanban_id = self.env.ref(
            'activities_board.boards_activities_kanban_view').id
        view_form_id = self.env.ref(
            'activities_done.boards_activities_form_view').id
        view_tree_id = self.env.ref(
            'activities_done.boards_activities_tree_view').id

        action = self.env.ref(
            'activities_board.open_boards_activities_form_tree').read()[0]
        action['search_view_id'] = self.env.ref(
            'activities_done.mail_activity_view_search').id
        action['views'] = [[view_tree_id, 'tree'],
                           [view_form_id, 'form'],
                           [view_kanban_id, 'kanban'],
                           [False, 'calendar'],
                           [False, 'pivot'],
                           [False, 'graph']]
        action_context = safe_eval(action['context'], {'uid': self.env.uid})
        action_context['search_default_all'] = 1
        action['context'] = action_context
        return action
