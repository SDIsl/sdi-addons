###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    move_ids = fields.One2many(
        comodel_name='project.task.analytics.move',
        inverse_name='project_task_id',
        string='Movements',
    )
    actual_time = fields.Float(
        string='Time in actual Stage',
        compute='_compute_actual_time',
        digits=(16, 2),
        store=True,
        help='The total time a project task spends in a stage.',
    )

    @api.depends('stage_id')
    def _compute_actual_time(self):
        for task in self:
            if not task.stage_id.is_closed and task.stage_id and \
                not task.project_id.is_template and \
                    not task.project_id.project_status.is_closed:
                for move in task.move_ids:
                    if not move.after_stage_id:
                        move._compute_updated_statistics_fields()
                task.actual_time = sum([
                    m.time_days for m in task.move_ids
                    if task.stage_id == m.previous_stage_id])
            else:
                task.actual_time = 0

    @api.model
    def create(self, values):
        result = super().create(values)
        self.env['project.task.analytics.move'].create({
            'project_task_id': result.id,
            'previous_stage_id': result.stage_id.id
        })
        return result

    def write(self, values):
        for task in self:
            if 'stage_id' not in values:
                continue
            stage = self.env['project.task.type'].browse(
                values['stage_id'])
            if stage.initial is not True and stage.final is not True:
                self.env['project.task.analytics.move'].create({
                    'project_task_id': task.id,
                    'previous_stage_id': stage.id,
                })
            moves = task.move_ids.filtered(
                lambda m: m.previous_stage_id == task.stage_id)
            values['move_ids'] = [
                (1, m.id, {
                    'after_stage_id': stage.id,
                    'end_date': fields.Datetime.now()}) for m in moves]
        return super().write(values)
