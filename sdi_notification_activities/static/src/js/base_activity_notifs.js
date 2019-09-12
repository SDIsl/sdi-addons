odoo.define('activity_notifs.activity_notifs', function (require) {
"use strict";

var bus = require('bus.bus').bus;
var BasicModel = require('web.BasicModel');
var field_registry = require('web.field_registry');
var Notification = require('web.notification').Notification;
var relational_fields = require('web.relational_fields');
var session = require('web.session');
var WebClient = require('web.WebClient');


var ActivityNotification = Notification.extend({
    template: "ActivityNotification",

    init: function(parent, title, text, eid) {
        this._super(parent, title, text, true);
        this.eid = eid;

        this.events = _.extend(this.events || {}, {
            'click .link2showed': function() {
                this.destroy(true);
                this._rpc({route: '/activity_following/notify_ack',params: {eid: eid},}
                    );
            },
        });
    },
});

WebClient.include({
    display_activity_following_notif: function(notifications) {
        var self = this;

        // For each notification, set a timeout to display it
        _.each(notifications, function(notif) {
           var notification = new ActivityNotification(self.notification_manager, notif.title, notif.message, notif.eid, notif.origin);
           self.notification_manager.display(notification);

        });

    },
    get_next_activity_following_notif: function() {
        session.rpc("/activity_following/notify", {}, {shadow: true})
            .done(
            this.display_activity_following_notif.bind(this)).fail(function(err, ev) {
                if(err.code === -32098) {
                    // Prevent the CrashManager to display an error
                    // in case of an xhr error not due to a server error
                    ev.preventDefault();
                }
            });
    },
    show_application: function() {
        // An event is triggered on the bus each time a calendar event with alarm
        // in which the current user is involved is created, edited or deleted
        this.calendar_notif_timeouts = {};
        this.calendar_notif = {};
        bus.on('notification', this, function (notifications) {
            _.each(notifications, (function (notification) {
                if (notification[0][1] === 'mail.activity.notifs') {
                    this.display_activity_following_notif(notification[1]);
                }
            }).bind(this));
        });
        return this._super.apply(this, arguments).then(this.get_next_activity_following_notif.bind(this));
    },
});

});
