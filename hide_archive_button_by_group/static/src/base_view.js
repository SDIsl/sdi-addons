odoo.define('hide_archive_button_by_group.BasicView', function (require) {
    "use strict";
    
    var session = require('web.session');
    var BasicView = require('web.BasicView');
    BasicView.include({
            init: function(viewInfo, params) {
                var self = this;
                this._super.apply(this, arguments);
                var model = self.controllerParams.modelName in ['res.partner'] ? 'True' : 'False';
                if(model) {
                    session.user_has_group('hide_archive_button_by_group.group_can_archive').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                }
            },
        });
    });
