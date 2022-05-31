###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models

SECONDS_PER_DAY = 86400


class ProjectTaskAnalyticsMove(models.Model):
    _name = 'project.task.analytics.move'
    _description = 'Saves the movement of project task and time at each stage'
    _order = 'create_date'

    project_task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
    )
    previous_stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Origin Stage',
        help='Stage previous the change.',
    )
    after_stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='End Stage',
        help='Stage after the change.',
    )
    end_date = fields.Datetime(
        string='End Date',
    )
    user_id_ref = fields.Many2one(
        related='project_task_id.user_id',
        string='Assigned to',
        readonly=True,
        store=True,
    )
    time_days = fields.Float(
        string='Time',
        digits=(16, 5),
        help='The days the project tasl has been in the initial stage.',
    )
    avg_stage_time = fields.Float(
        digits=(16, 5),
        group_operator='avg',
        help='The average time a project task spends in total.',
        string='AVG',
    )

    @api.multi
    @api.depends('end_date', 'after_stage_id')
    def _compute_updated_statistics_fields(self):
        for move in self:
            if not move.after_stage_id:
                move.end_date = fields.datetime.now()
            if not move.end_date:
                continue
            end = fields.Datetime.from_string(move.end_date)
            ini = fields.Datetime.from_string(move.create_date)
            aux = end - ini
            diff = aux.days + (aux.seconds / SECONDS_PER_DAY)
            move.write({
                'time_days': diff,
                'avg_stage_time': diff
            })
