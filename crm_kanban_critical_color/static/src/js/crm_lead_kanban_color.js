odoo.define('crm_kanban_critical_color.change_color_kanban', function (require) {
    "use strict"
    var KanbanRecord = require('web.KanbanRecord')
    KanbanRecord.include({
        _render: function () {
            let re = this._super()
            if (this.modelName == 'crm.lead') {
                if (this.record.date_deadline && this.record.date_deadline.value != '') {
                    this.$el.css('background-color', 'white')
                    var parts = this.record.date_deadline.value.split('/')
                    var deadline = new Date(parts[2], parts[1] - 1, parts[0])
                    var timeDiff = deadline - Date.now()
                    var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24))
                    if (diffDays <= -1 ) {
                        this.$el.css('background-color', '#ffcccc')
                    }
                }
            }
            return re
        },
    });
});
