###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def create(self, vals):
        user_id = self.env['res.users'].browse(self._context['uid'])
        if not user_id.project_task_disable_auto_subscribe:
            return super().create(vals)
        return super(ProjectTask, self.with_context(
            mail_create_nosubscribe=True)).create(vals)
