###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models

SECONDS_PER_DAY = 86400


class CrmAnalitycsMove(models.Model):
    _name = 'crm.analitycs.move'
    _description = 'save the movement of opportunities and time at each stage'
    _order = 'previous_stage_id desc, create_date desc'

    opportunity_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Oppotunity',
    )
    previous_stage_id = fields.Many2one(
        comodel_name='crm.stage',
        string='Origin Stage',
        help='Stage previous the change.',
    )
    after_stage_id = fields.Many2one(
        comodel_name='crm.stage',
        string='endal Stage',
        help='Stage after the change.',
    )
    end_date = fields.Datetime(
        string='End Date',
    )
    user_id_ref = fields.Many2one(
        related='opportunity_id.user_id',
        string='Salesman',
        readonly=True,
        store=True,
    )
    time_days = fields.Float(
        string='Time',
        digits=(16, 5),
        help='The days the opportunity has been in the initial stage.',
        compute='_compute_updated_stadistics_fields',
    )
    avg_stage_time = fields.Float(
        digits=(16, 5),
        group_operator='avg',
        help='The average time an opportunity spends in total.',
        string='AVG',
        compute='_compute_updated_stadistics_fields',
    )

    @api.depends('end_date', 'after_stage_id')
    def _compute_updated_stadistics_fields(self):
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
