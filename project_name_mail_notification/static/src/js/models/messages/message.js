odoo.define('project_name_mail_notification.model.Message', function (require) {
    "use strict";

    var Message = require('mail.model.Message');

    Message.include({
        /**
         * Return the values for the message's project task's project.
         */
        setProject: function (project) {
            if (project && project.id && project.name) {
                this._projectID = project.id;
                this._projectName = '( '.concat(project.name, ' ) ');
                $('a[data-oe-model="' + 'project.project' + '"][href="' + this.getURL() + '"]').attr('data-oe-id', project.id).text('( '.concat(project.name, ' ) '));
            }
        },
        /**
         * State whether this message's document is a project task
         * 
         * @returns {boolean}
         */
        hasProjectTask: function () {
            return this.getDocumentModel() === 'project.task';
        },
        /**
         * Get the ID of the document's project that this message is linked.
         *
         * @return {integer}
         */
        getProjectID: function () {
            return this._projectID;
        },
        /**
         * Get the name of the document's project that this message is linked.
         *
         * @return {string}
         */
        getProjectName: function () {
            return this._projectName;
        },
    });

});
