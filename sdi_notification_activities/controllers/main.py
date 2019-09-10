# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import registry as registry_get


class MailActivityFollowingController(http.Controller):

    # Function used, in RPC to check every 5 minutes, if notification to do for an event or not
    @http.route('/activity_following/notify', type='json', auth="user")
    def notify(self):
        return request.env['mail.activity.notifs'].get_next_notif()


    @http.route('/activity_following/notify_ack', type='json', auth="user")
    def notify_ack(self, eid):
        print (eid)
        return request.env['mail.activity.notifs']._set_notif_ack(eid)

