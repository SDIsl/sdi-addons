odoo.define('mail_activity_cancel.create_note_thread', function (require){
    "use strict";
    var Activity = require('mail.Activity')

    Activity.include({
        events: _.extend({}, Activity.prototype.events, {
            'click .o_message_activity_cancel': 'o_activity_cancel',
        }),
        o_activity_cancel: function (ev) {
            ev.preventDefault();
            var activityID = $(ev.currentTarget).data('activity-id')
            return this._rpc({
                model: 'mail.activity',
                method: 'action_cancel',
                args: [[activityID]],
                context: this.record.getContext(),
            })
            .then(this._reload.bind(this, { activity: true, thread: true }))
        }
    })
})
