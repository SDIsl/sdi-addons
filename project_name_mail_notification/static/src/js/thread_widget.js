odoo.define('project_name_mail_notification.widget.Thread', function (require) {
    "use strict";

    var ThreadWidget = require('mail.widget.Thread');

    ThreadWidget.include({
        render: function (thread, options) {
            if (!thread._documentModel && thread._type == 'mailbox') {
                let project_task_messages = thread.getMessages({ domain: options.domain || [] }).filter(message => message.hasProjectTask());
                if (project_task_messages.length > 0) {
                    let projectTaskIds = [...new Set(project_task_messages.map(message => message.getDocumentID()))];
                    this._rpc({
                        model: 'project.task',
                        method: 'search_read',
                        args: [[['id', 'in', projectTaskIds]]]
                    }).then((tasks) => {
                        _.each(tasks, function (task) {
                            let project = {'id': task.project_id[0], 'name': task.project_id[1]};
                            _.each(project_task_messages.filter(message => message.getDocumentID() == task.id), (message) => message.setProject(project));
                        });
                    });
                }
            }
            this._super.apply(this, arguments);
        }
    });

});
