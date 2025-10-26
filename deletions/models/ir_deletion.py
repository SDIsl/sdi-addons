from odoo import models, fields

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class IRDeletion(models.Model):
    _name = 'ir.deletion'
    _description = 'IR Deletion'

    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True)
    sql_statement = fields.Text(string='SQL Statement', required=True)
    sql_count_statement = fields.Text(string='SQL Count Statement')
    active = fields.Boolean(string='Active', default=False)
    log_ids = fields.One2many('ir.deletion.log', 'deletion_id', string='Logs')
    limit = fields.Integer(string='Limit', default=100)
    last_elapsed_time = fields.Float(string='Last Elapsed Time', readonly=True)
    last_count = fields.Integer(string='Pending', readonly=True)

    def validate_time(self):
        start_time = self.env['ir.config_parameter'].sudo().get_param(
            'ir.deletion.start_time')
        end_time = self.env['ir.config_parameter'].sudo().get_param(
            'ir.deletion.end_time')
        if start_time and end_time:
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()
            current_time = datetime.now().time()

            if not (start_time <= current_time <= end_time):
                _logger.info(
                    'Current time is outside the allowed range'
                    ' {} - {}. Modify config parameters.'
                    .format(start_time, end_time))
                return False
        else:
            _logger.info('Start time or end time is not set. '
                         'Logs will not be created or modified.')
            return False
        return True

    def process_deletions(self):
        today = fields.Date.today()

        if not self.validate_time():
            return

        for record in self.search([('active', '=', True)]):
            try:
                with self.env.cr.savepoint():
                    log = self.env['ir.deletion.log'].search([
                        ('deletion_id', '=', record.id),
                        ('date', '=', today)], limit=1)
                    if record.sql_count_statement:
                        self.env.cr.execute(record.sql_count_statement)
                        initial_count = self.env.cr.fetchone()[0]
                    else:
                        initial_count = self.env[
                            record.model_id.model].search_count([])
                    if not log:
                        log = self.env['ir.deletion.log'].create({
                            'deletion_id': record.id,
                            'date': today,
                            'initial_count': initial_count,
                        })
                    if initial_count:
                        record.with_delay().process_deletion(
                            record.model_id.id, record.id)
            except Exception as e:
                _logger.error('Error processing deletion: %s' % e)

    def process_deletion(self, model_id=False, id=False):
        if not self.validate_time():
            return
        if not model_id or not id:
            self.ensure_one()
            id = self.id
            model_id = self.model_id.id
        start_datetime = datetime.now()
        model_name = self.env['ir.model'].browse(model_id).model
        deletion_id = self.env['ir.deletion'].browse(id)
        try:
            with self.env.cr.savepoint():
                self.env.cr.execute(
                    deletion_id.sql_statement + ' LIMIT %s', (self.limit,))
                for record in self.env.cr.dictfetchall():
                    _logger.info('Deleting %s with ID: %s' % (
                        model_name, record['id']))
                    model_id = self.env[model_name].browse(record['id'])
                    if model_id:
                        model_id.unlink()
                last_elapsed_time = (
                        datetime.now() - start_datetime).total_seconds()
                final_count = 0
                if deletion_id.sql_count_statement:
                    self.env.cr.execute(deletion_id.sql_count_statement)
                    final_count = self.env.cr.fetchone()[0]
                else:
                    final_count = self.env[
                        deletion_id.model_id.model].search_count([])

                log_id = self.env['ir.deletion.log'].search([
                    ('deletion_id', '=', id),
                    ('date', '=', fields.Date.today())
                ], limit=1)
                log_id.write({
                    'final_count': final_count,
                })
                log_id.deletion_id.write({
                    'last_elapsed_time': last_elapsed_time,
                    'last_count': final_count,
                })
        except Exception as e:
            _logger.error('Error during deletion process: %s' % e)

    def action_view_logs(self):
        action = self.env.ref('deletions.action_view_logs').read()[0]
        action['domain'] = [('deletion_id', '=', self.id)]
        return action
