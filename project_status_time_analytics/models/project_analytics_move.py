###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models

SECONDS_PER_DAY = 86400


class ProjectAnalyticsMove(models.Model):
    _name = 'project.analytics.move'
    _description = 'Saves the movement of projects and time at each status'
    _order = 'create_date'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )
    previous_status_id = fields.Many2one(
        comodel_name='project.status',
        string='Origin Status',
        help='Status previous the change.',
    )
    after_status_id = fields.Many2one(
        comodel_name='project.status',
        string='End Status',
        help='Status after the change.',
    )
    end_date = fields.Datetime(
        string='End Date',
    )
    user_id_ref = fields.Many2one(
        related='project_id.user_id',
        string='Project Manager',
        readonly=True,
        store=True,
    )
    time_days = fields.Float(
        string='Time',
        digits=(16, 5),
        help='The days the project has been in the initial status.',
        compute='_compute_updated_statistics_fields',
    )
    avg_status_time = fields.Float(
        digits=(16, 5),
        group_operator='avg',
        help='The average time a project spends in total.',
        string='AVG',
        compute='_compute_updated_statistics_fields',
    )

    @api.depends('end_date', 'after_status_id')
    def _compute_updated_statistics_fields(self):
        for move in self:
            if not move.after_status_id:
                move.end_date = fields.datetime.now()
            if not move.end_date:
                continue
            end = fields.Datetime.from_string(move.end_date)
            ini = fields.Datetime.from_string(move.create_date)
            aux = end - ini
            diff = aux.days + (aux.seconds / SECONDS_PER_DAY)
            move.write({
                'time_days': diff,
                'avg_status_time': diff
            })
