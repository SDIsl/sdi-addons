odoo.define('sdi.systray', function (require) {
"use strict";

    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var actMenu = require('mail.systray');
    var chat_manager = require('mail.chat_manager');

    var QWeb = core.qweb;

    var sdiMessagingMenu;

    for (var i = 0; i < SystrayMenu.Items.length; i++) {
        if (SystrayMenu.Items[i].prototype.template=='mail.chat.MessagingMenu'){
            sdiMessagingMenu = SystrayMenu.Items[i];
            sdiMessagingMenu.include({

                // Handlers

                /**
                 * When a channel is clicked on, we want to open chat/channel window
                 *
                 * @private
                 * @param {MouseEvent} event
                 */
                _onClickChannel: function (event) {
                    var self = this;
                    var channelID = $(event.currentTarget).data('channel_id');
                    if (channelID === 'channel_inbox') {
                        var resID = $(event.currentTarget).data('res_id');
                        var resModel = $(event.currentTarget).data('res_model');
                        if (resModel && resID) {

                            var resFormId = $(event.currentTarget).data('form_id') ? $(event.currentTarget).data('form_id') : false;

                            this.do_action({
                                type: 'ir.actions.act_window',
                                res_model: resModel,
                                views: [[resFormId, 'form']],
                                res_id: resID
                            });
                        } else {
                            this.do_action('mail.mail_channel_action_client_chat', {clear_breadcrumbs: true})
                                .then(function () {
                                    self.trigger_up('hide_app_switcher');
                                    core.bus.trigger('change_menu_section', chat_manager.get_discuss_menu_id());
                                });
                        }
                    } else {
                        var channel = chat_manager.get_channel(channelID);
                        if (channel) {
                            chat_manager.open_channel(channel);
                        }
                    }
                },

            });
            break;
        }
    }

    var activityItem = actMenu.ActivityMenu.include({

        // Handlers

        /**
         * override
         * Redirect to particular model view
         * @private
         * @param {MouseEvent} event
         */
        _onActivityFilterClick: function (event) {
            var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());

            var kanban_id = false,
                form_id = false,
                search_id = false;
            if (data.res_model=="crm.lead"){
                kanban_id = data.kanban_id;
                form_id = data.form_id;
                search_id = data.search_id;
            }

            var context = {};
            if (data.filter === 'my') {
                context['search_default_activities_overdue'] = 1;
                context['search_default_activities_today'] = 1;
            } else {
                context['search_default_activities_' + data.filter] = 1;
            }

            var params = {
                type: 'ir.actions.act_window',
                name: data.model_name,
                res_model:  data.res_model,
                views: [[kanban_id, 'kanban'], [form_id, 'form']],
                search_view_id: [search_id],
                domain: [['activity_user_id', '=', session.uid]],
                context:context,
            }

            if (data.res_model=="crm.lead"){
                params['domain'].push(['type', '=', data.model_name]);
                params['context']['default_type'] = data.model_name;
            };

            this.do_action(params);
        },

    });

    return {
        ActivityMenu: activityItem,
    };

});
