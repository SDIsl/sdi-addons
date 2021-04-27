# -*- coding: utf-8 -*-
from odoo import api, fields, models
import pytz
import datetime
from datetime import timedelta


class ActivityPlanning(models.Model):
    _name = "activity.planning"
    _description = "Task Cron Registers"

    def get_days_of_month(self):
        days_list = []
        for i in range(1, 31):
            days_list.append((str(i), str(i)))
        return days_list

    active = fields.Boolean(default=True)
    name = fields.Char(string='Name of the planned activities',
                       track_visibility='always', required=True, index=True)
    user_ids = fields.Many2many('res.users', string='Users')
    recurrent = fields.Selection([
        ('0', 'Daily'),
        ('1', 'Weekly'),
        ('2', 'Monthly'),
        ('3', 'Days of week')],
        default='0',
        index=True,
        string="Frequency"
    )
    recurrent_monday = fields.Boolean("Monday")
    recurrent_tuesday = fields.Boolean("Tuesday")
    recurrent_wednesday = fields.Boolean("Wednesday")
    recurrent_thursday = fields.Boolean("Thursday")
    recurrent_friday = fields.Boolean("Friday")
    recurrent_saturday = fields.Boolean("Saturday")
    recurrent_sunday = fields.Boolean("Sunday")
    recurrent_day_of_week = fields.Selection([('1', 'Monday'),
                                              ('2', 'Tuesday'),
                                              ('3', 'Wednesday'),
                                              ('4', 'Thursday'),
                                              ('5', 'Friday'),
                                              ('6', 'Saturday'),
                                              ('7', 'Sunday')],
                                             default='1', string="Day of week")
    recurrent_day_of_month = fields.Selection(get_days_of_month,
                                              string="Day of month",
                                              default='1')
    cron_activity_ids = fields.One2many(
        'template.cron.activity', 'res_id', 'Activities',
        auto_join=True)
    date_start = fields.Date("Date start")
    date_end = fields.Date("Date end")

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active``
        on the records in ``self``. """
        for record in self:
            record.active = not record.active

    @api.model
    def cron_create_activities(self):
        print("OK Create activities")
        tasks_obj = self.env['activity.planning']
        activities_obj = self.env['template.cron.activity']
        calendar_obj = self.env['resource.calendar.leaves']
        today = datetime.date.today()
        time = datetime.datetime.now()
        tasks = tasks_obj.search([
            '|', ('date_start', '=', False), ('date_start', '<=', today),
            '|', ('date_end', '=', False), ('date_end', '>=', today),
            ('active', '=', True)])
        print(today.weekday())
        global_leaves = calendar_obj.search([
            ('date_from', '<=', str(time)), ('date_to', '>=', str(time)),
            ('resource_id', '=', False)], limit=1)
        if (global_leaves):
            print("Festivo")
        else:
            for task in tasks:
                if ((task.recurrent == '1' and
                    task.recurrent_day_of_week == str(today.weekday() + 1)) or
                    (task.recurrent == '0' and today.weekday() < 5) or
                    (task.recurrent == '2' and
                    task.recurrent_day_of_month == str(today.strftime("%d"))
                     ) or
                    (task.recurrent == '3' and
                    ((task.recurrent_monday and today.weekday() == 0) or
                        (task.recurrent_tuesday and today.weekday() == 1) or
                        (task.recurrent_wednesday and today.weekday() == 2) or
                        (task.recurrent_thursday and today.weekday() == 3) or
                        (task.recurrent_friday and today.weekday() == 4) or
                        (task.recurrent_saturday and today.weekday() == 5) or
                        (task.recurrent_sunday and today.weekday() == 6)))):
                    activities = activities_obj.search(
                        [('res_id', '=', task.id)], order='sequence')
                    for user in task.user_ids:
                        leave = False
                        if (not leave):
                            print(user.name)
                            activity_id = False
                            for activity in activities:
                                print(activity.summary)
                                res = {
                                    'summary': activity.summary,
                                    'activity_type_id':
                                    activity.activity_type_id.id,
                                    'res_id': user.partner_id.id,
                                    'user_id': user.id,
                                    'date_deadline': today,
                                    'res_model_id':
                                    self.env.ref('base.model_res_partner').id,
                                }
                                if (activity.depend_before and activity_id):
                                    res['depend_activity_id'] = activity_id.id
                                activity_id = \
                                    self.env['mail.activity'].create(res)
        return True


class CronActivityTemplate(models.Model):
    _name = 'template.cron.activity'
    _description = 'Activity Cron Lines'
    _order = "sequence, id"

    res_id = fields.Many2one('activity.planning', string="Cron Task Reference",
                             required=True, ondelete='cascade', index=True,
                             copy=False)
    # activity
    activity_type_id = fields.Many2one(
        'mail.activity.type', 'Type of Activity',
        domain=lambda self: ['|', ('res_model_id', '=', False)],
        required=True)
    summary = fields.Char(string='Summary', required=True)
    sequence = fields.Integer("Sequence")
    depend_before = fields.Boolean('Depend before')
