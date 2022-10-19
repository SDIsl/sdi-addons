###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    move_ids = fields.One2many(
        comodel_name='crm.analitycs.move',
        inverse_name='opportunity_id',
        string='Movements',
    )
    actual_time = fields.Float(
        string='Time in actual Stage',
        compute='_compute_actual_time',
        digits=(16, 2),
        store=True,
        help='The total time an opportunity spends in a stage ().',
    )

    @api.depends('stage_id')
    def _compute_actual_time(self):
        for lead in self:
            for move in lead.move_ids:
                if not move.after_stage_id:
                    move._compute_updated_stadistics_fields()
            lead.actual_time = sum([
                m.time_days for m in lead.move_ids
                if lead.stage_id == m.previous_stage_id])

    @api.model
    def create(self, values):
        result = super().create(values)
        self.env['crm.analitycs.move'].create({
            'opportunity_id': result.id,
            'previous_stage_id': result.stage_id.id
        })
        return result

    def write(self, values):
        for lead in self:
            if 'stage_id' not in values:
                continue
            stage = self.env['crm.stage'].browse(values['stage_id'])
            if stage.initial is not True and stage.final is not True:
                self.env['crm.analitycs.move'].create({
                    'opportunity_id': lead.id,
                    'previous_stage_id': stage.id,
                })
            moves = lead.move_ids.filtered(
                lambda m: m.previous_stage_id == lead.stage_id)
            values['move_ids'] = [
                (1, m.id, {
                    'after_stage_id': stage.id,
                    'end_date': fields.Datetime.now()}) for m in moves]
        return super().write(values)
