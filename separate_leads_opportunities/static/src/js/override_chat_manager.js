odoo.define('sdi.mail.chat_manager', function (require) {
"use strict";

    var session = require('web.session');
    var chat_manager = require('mail.chat_manager');
    var utils = require('mail.utils');
    var time = require('web.time');
    var ODOOBOT_ID = "ODOOBOT";
    var emoji_substitutions = {};
    var channels_preview_def;
    var messages = [];

    function add_channel_to_message (message, channel_id) {
        message.channel_ids.push(channel_id);
        message.channel_ids = _.uniq(message.channel_ids);
    };

    function add_message (data, options) {
        options = options || {};
        var msg = _.findWhere(messages, { id: data.id });

        if (!msg) {
            msg = chat_manager.make_message(data);
            // Keep the array ordered by id when inserting the new message
            messages.splice(_.sortedIndex(messages, msg, 'id'), 0, msg);
            _.each(msg.channel_ids, function (channel_id) {
                var channel = chat_manager.get_channel(channel_id);
                if (channel) {
                    // update the channel's last message (displayed in the channel
                    // preview, in mobile)
                    if (!channel.last_message || msg.id > channel.last_message.id) {
                        channel.last_message = msg;
                    }
                    add_to_cache(msg, []);
                    if (options.domain && options.domain !== []) {
                        add_to_cache(msg, options.domain);
                    }
                    if (channel.hidden) {
                        channel.hidden = false;
                        chat_manager.bus.trigger('new_channel', channel);
                    }
                    if (channel.type !== 'static' && !msg.is_author && !msg.is_system_notification) {
                        if (options.increment_unread) {
                            update_channel_unread_counter(channel, channel.unread_counter+1);
                        }
                        if (channel.is_chat && options.show_notification) {
                            if (!client_action_open && !config.device.isMobile) {
                                // automatically open chat window
                                chat_manager.bus.trigger('open_chat', channel, { passively: true });
                            }
                            var query = {is_displayed: false};
                            chat_manager.bus.trigger('anyone_listening', channel, query);
                            notify_incoming_message(msg, query);
                        }
                    }
                }
            });
            if (!options.silent) {
                chat_manager.bus.trigger('new_message', msg);
            }
        } else if (options.domain && options.domain !== []) {
            add_to_cache(msg, options.domain);
        }
        return msg;
    };


    function add_to_cache(message, domain) {
        _.each(message.channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                var channel_cache = get_channel_cache(channel, domain);
                var index = _.sortedIndex(channel_cache.messages, message, 'id');
                if (channel_cache.messages[index] !== message) {
                    channel_cache.messages.splice(index, 0, message);
                }
            }
        });
    }

    function get_channel_cache (channel, domain) {
        var stringified_domain = JSON.stringify(domain || []);
        if (!channel.cache[stringified_domain]) {
            channel.cache[stringified_domain] = {
                all_history_loaded: false,
                loaded: false,
                messages: [],
            };
        }
        return channel.cache[stringified_domain];
    }
//----------------------------------------------------------------------------------

    function make_message (data) {
        var msg = {
            id: data.id,
            form_id: data.form_id,
            author_id: data.author_id,
            body: data.body || "",
            date: moment(time.str_to_datetime(data.date)),
            message_type: data.message_type,
            subtype_description: data.subtype_description,
            is_author: data.author_id && data.author_id[0] === session.partner_id,
            is_note: data.is_note,
            is_system_notification: (data.message_type === 'notification' && data.model === 'mail.channel')
                || data.info === 'transient_message',
            attachment_ids: data.attachment_ids || [],
            subject: data.subject,
            email_from: data.email_from,
            customer_email_status: data.customer_email_status,
            customer_email_data: data.customer_email_data,
            record_name: data.record_name,
            tracking_value_ids: data.tracking_value_ids,
            channel_ids: data.channel_ids,
            model: data.model,
            res_id: data.res_id,
            url: session.url("/mail/view?message_id=" + data.id),
            module_icon:data.module_icon,
        };

        _.each(_.keys(emoji_substitutions), function (key) {
            var escaped_key = String(key).replace(/([.*+?=^!:${}()|[\]\/\\])/g, '\\$1');
            var regexp = new RegExp("(?:^|\\s|<[a-z]*>)(" + escaped_key + ")(?=\\s|$|</[a-z]*>)", "g");
            msg.body = msg.body.replace(regexp, ' <span class="o_mail_emoji">'+emoji_substitutions[key]+'</span> ');
        });

        function property_descr(channel) {
            return {
                enumerable: true,
                get: function () {
                    return _.contains(msg.channel_ids, channel);
                },
                set: function (bool) {
                    if (bool) {
                        add_channel_to_message(msg, channel);
                    } else {
                        msg.channel_ids = _.without(msg.channel_ids, channel);
                    }
                }
            };
        }

        Object.defineProperties(msg, {
            is_starred: property_descr("channel_starred"),
            is_needaction: property_descr("channel_inbox"),
        });

        if (_.contains(data.needaction_partner_ids, session.partner_id)) {
            msg.is_needaction = true;
        }
        if (_.contains(data.starred_partner_ids, session.partner_id)) {
            msg.is_starred = true;
        }
        if (msg.model === 'mail.channel') {
            var real_channels = _.without(msg.channel_ids, 'channel_inbox', 'channel_starred');
            var origin = real_channels.length === 1 ? real_channels[0] : undefined;
            var channel = origin && chat_manager.get_channel(origin);
            if (channel) {
                msg.origin_id = origin;
                msg.origin_name = channel.name;
            }
        }

        // Compute displayed author name or email
        if ((!msg.author_id || !msg.author_id[0]) && msg.email_from) {
            msg.mailto = msg.email_from;
        } else {
            msg.displayed_author = (msg.author_id === ODOOBOT_ID) && "OdooBot" ||
                                   msg.author_id && msg.author_id[1] ||
                                   msg.email_from || _t('Anonymous');
        }

        // Don't redirect on author clicked of self-posted or OdooBot messages
        msg.author_redirect = !msg.is_author && msg.author_id !== ODOOBOT_ID;

        // Compute the avatar_url
        if (msg.author_id === ODOOBOT_ID) {
            msg.avatar_src = "/mail/static/src/img/odoo_o.png";
        } else if (msg.author_id && msg.author_id[0]) {
            msg.avatar_src = "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
        } else if (msg.message_type === 'email') {
            msg.avatar_src = "/mail/static/src/img/email_icon.png";
        } else {
            msg.avatar_src = "/mail/static/src/img/smiley/avatar.jpg";
        }

        // add anchor tags to urls
        msg.body = utils.parse_and_transform(msg.body, utils.add_link);

        // Compute url of attachments
        _.each(msg.attachment_ids, function(a) {
            a.url = '/web/content/' + a.id + '?download=true';
        });

        // format date to the local only once by message
        // can not be done in preprocess, since it alter the original value
        if (msg.tracking_value_ids && msg.tracking_value_ids.length) {
            _.each(msg.tracking_value_ids, function(f) {
                if (f.field_type === 'datetime') {
                    var format = 'LLL';
                    if (f.old_value) {
                        f.old_value = moment.utc(f.old_value).local().format(format);
                    }
                    if (f.new_value) {
                        f.new_value = moment.utc(f.new_value).local().format(format);
                    }
                } else if (f.field_type === 'date') {
                    var format = 'LL';
                    if (f.old_value) {
                        f.old_value = moment(f.old_value).local().format(format);
                    }
                    if (f.new_value) {
                        f.new_value = moment(f.new_value).local().format(format);
                    }
                }
            });
        }

        return msg;
    };

    function get_channels_preview (channels) {
        var channels_preview = _.map(channels, function (channel) {
            var info;
            if (channel.channel_ids && _.contains(channel.channel_ids,"channel_inbox")) {
                // map inbox(mail_message) data with existing channel/chat template
                info = _.pick(channel, 'form_id', 'id', 'body', 'avatar_src', 'res_id', 'model', 'module_icon', 'subject','date', 'record_name', 'status', 'displayed_author', 'email_from', 'unread_counter');
                info.last_message = {
                    body: info.body,
                    date: info.date,
                    displayed_author: info.displayed_author || info.email_from,
                };
                info.name = info.record_name || info.subject || info.displayed_author;
                info.image_src = info.module_icon || info.avatar_src;
                info.message_id = info.id;
                info.id = 'channel_inbox';
                return info;
            }
            info = _.pick(channel, 'id', 'is_chat', 'name', 'status', 'unread_counter');
            info.last_message = channel.last_message || _.last(channel.cache['[]'].messages);
            if (!info.is_chat) {
                info.image_src = '/web/image/mail.channel/'+channel.id+'/image_small';
            } else if (channel.direct_partner_id) {
                info.image_src = '/web/image/res.partner/'+channel.direct_partner_id+'/image_small';
            } else {
                info.image_src = '/mail/static/src/img/smiley/avatar.jpg';
            }
            return info;
        });
        var missing_channels = _.where(channels_preview, {last_message: undefined});
        if (!channels_preview_def) {
            if (missing_channels.length) {
                var missing_channel_ids = _.pluck(missing_channels, 'id');
                channels_preview_def = this._rpc({
                        model: 'mail.channel',
                        method: 'channel_fetch_preview',
                        args: [missing_channel_ids],
                    }, {
                        shadow: true,
                    });
            } else {
                channels_preview_def = $.when();
            }
        }
        return channels_preview_def.then(function (channels) {
            _.each(missing_channels, function (channel_preview) {
                var channel = _.findWhere(channels, {id: channel_preview.id});
                if (channel) {
                    channel_preview.last_message = add_message(channel.last_message);
                }
            });
            // sort channels: 1. unread, 2. chat, 3. date of last msg
            channels_preview.sort(function (c1, c2) {
                return Math.min(1, c2.unread_counter) - Math.min(1, c1.unread_counter) ||
                       c2.is_chat - c1.is_chat ||
                       !!c2.last_message - !!c1.last_message ||
                       (c2.last_message && c2.last_message.date.diff(c1.last_message.date));
            });

            // generate last message preview (inline message body and compute date to display)
            _.each(channels_preview, function (channel) {
                if (channel.last_message) {
                    channel.last_message_preview = chat_manager.get_message_body_preview(channel.last_message.body);
                    channel.last_message_date = channel.last_message.date.fromNow();
                }
            });
            return channels_preview;
        });
    };

    chat_manager.__proto__.make_message = make_message;

    chat_manager.__proto__.get_channels_preview = get_channels_preview;

});
