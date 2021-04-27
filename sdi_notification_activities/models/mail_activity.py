# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import pytz
from datetime import datetime
from datetime import timedelta


class MailActivity(models.Model):
    _inherit = "mail.activity"

    # Following activities
    following_time = fields.Float(
        string="Hora del fin del seguimiento",
        index=True,
        help="""It specifies the time at which the monitoring will be stopped,
                therefore, the time at which the activity will expire.""")
    following_notification_done = fields.Boolean("Done Notification")
    following_notification_minutes_before = fields.Integer(
        "Minutes Before Notification")
    following_notification_minutes_before_check = fields.Boolean(
        "Minutes Before Notification Check", default=True)
    following_notification_expired = fields.Boolean(
        "Expired Notification")
    following_notification_user_ids = fields.Many2many(
        "res.users",
        relation="res_user_following_notification_user_ids",
        string="Notification Users",
        help="""Select the users who will receive notifications of this
                activity.""")
    following_notification_notif_modes = fields.Selection(
        string="Type of notification",
        selection=[
            ('inbox', 'Inbox'),
            ('popup', 'Pop-Up'),
            ('both', 'Both')
        ],
        required=False,
        default="inbox",
        help="""Select the type of notification
            Inbox: The notification will be sent to the user's email.
            Pop-up: The notification will be received by means of a warning
            upon entering odoo.
            Both: The notification will be done both ways.""")

    def cron_following_activity_notifications(self):
        today = datetime.today()
        madrid = pytz.timezone('Europe/Madrid')
        print(today)
        now = datetime.utcnow()
        now = madrid.fromutc(now).replace(tzinfo=None)
        print(now)
        activities = self.env['mail.activity'].search([
            ('following_time', '!=', 0.0), ('date_deadline', '=', today)])
        for activity in activities:
            following_time = activity.following_time
            print(activity.following_time)
            hours = int(following_time)
            minutes = int((following_time - hours) * 60)
            date_deadline = fields.Date.from_string(activity.date_deadline)
            activitydate = datetime(date_deadline.year, date_deadline.month,
                                    date_deadline.day, hours, minutes)
            print("Date: " + str(activitydate))
            notify = False
            model = self.env[activity.res_model].search([
                ('id', '=', activity.res_id)], limit=1)
            notify_message = ""
            if (model and model.name):
                notify_message += "Origen: " + model.name + "<br>"
            notify_message += "Asignada a : " + activity.user_id.name + "<br>"
            if (activity.summary):
                notify_message += "Resumen: " + activity.summary + "<br>"
            if activity.following_notification_expired and now > activitydate:
                activity.write({'following_notification_expired': False})
                notify = True
                notify_message += \
                    "La actividad ha expirado en " + str(activitydate)
            if not notify and \
               activity.following_notification_minutes_before_check and \
               now >= activitydate - timedelta(
                   minutes=activity.following_notification_minutes_before):
                activity.write({
                    'following_notification_minutes_before_check': False
                })
                notify = True
                notify_message += \
                    "La actividad expirará en " + str(activitydate)
            if (notify):
                print(notify_message)
                array_users = [activity.user_id.partner_id.id]
                for follower_id in activity.following_notification_user_ids:
                    array_users.append(follower_id.partner_id.id)
                notifications = []
                for partner_id in array_users:
                    notify_bus = {
                        'title': activity.activity_type_id.name,
                        'message': notify_message,
                        'partner_id': partner_id
                    }
                    if activity.following_notification_notif_modes == \
                       'popup' or \
                       activity.following_notification_notif_modes == 'both':
                        notif = self.env[
                            'mail.activity.notifs'].create(notify_bus)
                        notify_bus['eid'] = notif.id
                        del notify_bus["partner_id"]
                        notifications.append([(
                            self._cr.dbname,
                            'mail.activity.notifs',
                            partner_id
                        ), [notify_bus]])
                    if activity.following_notification_notif_modes == \
                       'popup' or \
                       activity.following_notification_notif_modes == 'both':
                        activity.user_id.partner_id.message_post(
                            body=notify_message,
                            subtype='mt_comment',
                            partner_ids=[[6, 0, [partner_id]]],
                        )

                if len(notifications) > 0:
                    print(notifications)
                    self.env['bus.bus'].sendmany(notifications)

        return True

    def action_feedback(self, feedback=False):
        for activity in self:
            if (activity.following_notification_done):
                model = self.env[activity.res_model].search([
                    ('id', '=', activity.res_id)], limit=1)
                notify_message = ""
                if (model and model.name):
                    notify_message += "Origen: " + model.name + "<br>"
                notify_message += "Asignada a : " + activity.user_id.name + \
                    "<br>"
                if (activity.summary):
                    notify_message += "Resumen: " + activity.summary + "<br>"
                notify_message += \
                    "La actividad ha sido realizada por : <br>" + \
                    self.user_id.name
                print(notify_message)
                array_users = [activity.user_id.partner_id.id]
                for follower_id in activity.following_notification_user_ids:
                    array_users.append(follower_id.partner_id.id)
                notifications = []
                for partner_id in array_users:
                    notify_bus = {'title': activity.activity_type_id.name,
                                  'message': notify_message,
                                  'partner_id': partner_id}
                    if activity.following_notification_notif_modes == \
                       'popup' or \
                       activity.following_notification_notif_modes == 'both':
                        notif = self.env['mail.activity.notifs'].create(
                            notify_bus)
                        notify_bus['eid'] = notif.id
                        del notify_bus["partner_id"]
                        notifications.append([(
                            self._cr.dbname,
                            'mail.activity.notifs',
                            partner_id
                        ), [notify_bus]])
                    if activity.following_notification_notif_modes == \
                       'inbox' or \
                       activity.following_notification_notif_modes == 'both':
                        activity.user_id.partner_id.message_post(
                            body=notify_message,
                            subtype='mt_comment',
                            partner_ids=[[6, 0, [partner_id]]],
                        )
                if len(notifications) > 0:
                    print(notifications)
                    self.env['bus.bus'].sendmany(notifications)

        return super(MailActivity, self).action_feedback(feedback)


class MailActivityNotifs(models.Model):
    _name = 'mail.activity.notifs'
    _description = 'Mail activity notifs'

    partner_id = fields.Many2one('res.partner', 'Partner', readonly="True")

    name = fields.Char('Name')
    message = fields.Char('Message')
    title = fields.Char('Title')
    duration = fields.Integer('Remind Before')

    @api.model
    def get_next_notif(self):
        partner_id = self.env.user.partner_id
        all_notif = []

        if not partner_id:
            return []
        for activity_notif in self.env['mail.activity.notifs'].search([
                ('partner_id', '=', partner_id.id)]):
            notify = {
                'title': activity_notif.title,
                'message': activity_notif.message,
                'eid': activity_notif.id}
            all_notif.append(notify)
        return all_notif

    @api.model
    def _set_notif_ack(self, eid):
        self.env['mail.activity.notifs'].search(
            [('id', '=', eid)], limit=1).unlink()
