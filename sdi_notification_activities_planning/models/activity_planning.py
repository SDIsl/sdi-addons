# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime


class ActivityPlanning(models.Model):
    _inherit = "activity.planning"

    following_time = fields.Float(
        "Time following",
        index=True,
    )
    following_notification_done = fields.Boolean(
        "Done Notification",
    )
    following_notification_minutes_before = fields.Integer(
        "Minutes Before Notification",
    )
    following_notification_minutes_before_check = fields.Boolean(
        "Minutes Before Notification Check",
        default=True,
    )
    following_notification_expired = fields.Boolean("Expired Notification")
    following_notification_user_ids = fields.Many2many(
        "res.users",
        relation="res_users_following_notification_user_ids",
        string="Notification Users",
    )
    following_notification_notif_modes = fields.Selection(
        string="Avisos a",
        selection=[
            ('inbox', 'Bandeja de entrada'),
            ('popup', 'Pop-Up'),
            ('both', 'Ambos')],
        required=False,
        default="inbox",
    )

    @api.model
    def cron_create_activities(self):
        print("OK Create activities")
        tasks_obj = self.env['activity.planning']
        activities_obj = self.env['template.cron.activity']
        calendar_obj = self.env['resource.calendar.leaves']
        today = datetime.date.today()
        time = datetime.datetime.now()
        tasks = tasks_obj.search(
            ['|', ('date_start', '=', False), ('date_start', '<=', today),
                '|', ('date_end', '=', False), ('date_end', '>=', today),
                ('active', '=', True)]
        )
        print(today.weekday())
        global_leaves = calendar_obj.search(
            [('date_from', '<=', str(time)),
                ('date_to', '>=', str(time)),
                ('resource_id', '=', False)], limit=1
        )
        if (global_leaves):
            print("Festivo")
        else:
            for task in tasks:
                fnmbc = task.following_notification_minutes_before_check
                fnui = task.following_notification_user_ids
                if ((task.recurrent == '1' and
                    task.recurrent_day_of_week == str(today.weekday() + 1)) or
                    (task.recurrent == '0' and today.weekday() < 5) or
                    (task.recurrent == '2' and
                        task.recurrent_day_of_month == str(
                            today.strftime("%d"))) or
                    (task.recurrent == '3' and (
                        (task.recurrent_monday and today.weekday() == 0) or
                        (task.recurrent_tuesday and today.weekday() == 1) or
                        (task.recurrent_wednesda and today.weekday() == 2) or
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
                                    'following_time': task.following_time,
                                    'following_notification_done':
                                    task.following_notification_done,
                                    'following_notification_minutes_before':
                                    task.following_notification_minutes_before,
                                    '''following_notification
                                    _minutes_before_check''': fnmbc,
                                    'following_notification_expired':
                                    task.following_notification_expired,
                                    'following_notification_user_ids':
                                    [(6, 0, [user.id for user in fnui])],
                                    'following_notification_notif_modes':
                                    task.following_notification_notif_modes,
                                }
                                if (activity.depend_before and activity_id):
                                    res['depend_activity_id'] = activity_id.id
                                activity_id = self.env[
                                    'mail.activity'].create(res)
        return True
