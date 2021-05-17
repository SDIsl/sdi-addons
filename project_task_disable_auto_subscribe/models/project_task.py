###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def create(self, vals):
        res = super().create(vals)
        for follower in res['message_follower_ids']:
            user = self.env['res.users'].search([
                ('partner_id', '=', follower.partner_id.id),
            ], limit=1,)
            if user.id == self.create_uid.id and \
               user.project_task_disable_auto_subscribe:
                self.env['mail.followers'].search([
                    ('id', '=', follower.id),
                ]).unlink()
        return res
