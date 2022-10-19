###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'

    move_ids = fields.One2many(
        comodel_name='project.analytics.move',
        inverse_name='project_id',
        string='Movements',
    )
    actual_time = fields.Float(
        string='Time in actual Status',
        compute='_compute_actual_time',
        digits=(16, 2),
        store=True,
        help='The total time a project spends in a status.',
    )

    @api.depends('project_status')
    def _compute_actual_time(self):
        for project in self:
            if not project.is_template and project.project_status and \
                    not project.project_status.is_closed:
                for move in project.move_ids:
                    if not move.after_status_id:
                        move._compute_updated_statistics_fields()
                project.actual_time = sum([
                    m.time_days for m in project.move_ids
                    if project.project_status == m.previous_status_id])
            else:
                project.actual_time = 0

    @api.model
    def create(self, values):
        result = super().create(values)
        self.env['project.analytics.move'].create({
            'project_id': result.id,
            'previous_status_id': result.project_status.id
        })
        return result

    def write(self, values):
        for project in self:
            if 'project_status' not in values:
                continue
            status = self.env['project.status'].browse(
                values['project_status'])
            if status.initial is not True and status.final is not True:
                self.env['project.analytics.move'].create({
                    'project_id': project.id,
                    'previous_status_id': status.id,
                })
            moves = project.move_ids.filtered(
                lambda m: m.previous_status_id == project.project_status)
            values['move_ids'] = [
                (1, m.id, {
                    'after_status_id': status.id,
                    'end_date': fields.Datetime.now()}) for m in moves]
        return super().write(values)
