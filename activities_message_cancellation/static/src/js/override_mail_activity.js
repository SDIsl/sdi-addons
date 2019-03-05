odoo.define('crm.cancel.activity', function (require){
"use strict";

var Activity = require('mail.Activity');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

Activity.include({

    events: {
        'click .o_activity_edit': '_onEditActivity',
        'click .o_activity_unlink': '_onUnlinkActivity',
        'click .o_activity_done': '_onMarkActivityDone',
        'click .o_activity_cancel': '_onCancelActivity',
    },
    /**
     *
     * @param {any} params
     * @returns {Deferred}
     */
    _onCancelActivity: function (event, options) {
        event.preventDefault();
        var self = this;
        var activity_id = $(event.currentTarget).data('activity-id');
        var activity = _.find(this.activities, function (act) { return act.id === activity_id; });

        if (activity && activity.activity_category === 'meeting' && activity.calendar_event_id)
        {
            Dialog.confirm
            (
                self,
                _t("The activity is linked to a meeting. Cancelling it will cancel the meeting as well. Do you want to proceed ?"), {
                    confirm_callback: function(){
                        self._cancelPopover(event);
                    }
                },
            );
        }
        else {
            self._cancelPopover(event);
        }
    },
    _markActivityCancel: function (id, feedback) {
            return this._rpc({
                    model: 'mail.activity',
                    method: 'action_cancel',
                    args: [[id]],
                    kwargs: {feedback: feedback},
                    context: this.record.getContext(),
                });
    },
    _cancelPopover: function(event){
        var self = this;
        var $popover_el = $(event.currentTarget);
        var activity_id = $popover_el.data('activity-id');

        if (!$popover_el.data('bs.popover')) {
            $popover_el.popover({
                title : _t('Feedback'),
                html: 'true',
                trigger:'click',
                content : function() {
                    var $popover = $(QWeb.render("mail.activity_feedback_cancel_form", {}));
                    $popover.on('click', '.o_activity_popover_cancel', function () {
                        var feedback = _.escape($popover.find('#activity_feedback').val());
                        self._markActivityCancel(activity_id, feedback)
                            .then(self._reload.bind(self, {activity: true, thread: true}));
                    });
                    $popover.on('click', '.o_activity_popover_discard', function () {
                        $popover_el.popover('hide');
                    });
                    return $popover;
                },
            }).on("show.bs.popover", function (e) {
                var $popover = $(this).data("bs.popover").tip();
                $popover.addClass('o_mail_activity_feedback').attr('tabindex', 0);
                $(".o_mail_activity_feedback.popover").not(e.target).popover("hide");
            }).on("shown.bs.popover", function () {
                var $popover = $(this).data("bs.popover").tip();
                $popover.find('#activity_feedback').focus();
                $popover.off('focusout');
                $popover.focusout(function (e) {
                    // outside click of popover hide the popover
                    // e.relatedTarget is the element receiving the focus
                    if(!$popover.is(e.relatedTarget) && !$popover.find(e.relatedTarget).length) {
                        $popover.popover('hide');
                    }
                });
            }).popover('show');
        }
    }

});

});
