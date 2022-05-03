###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models

from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    actual_calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        string='Actual calendar',
    )

    antiquity = fields.Integer(
        string='Antiquity',
        compute='_compute_antiquity',
    )

    @api.multi
    @api.depends('calendar_ids')
    def _compute_antiquity(self):
        today = date.today()
        days = 0
        for rec in self:
            for line in rec.calendar_ids:
                if line.date_start and line.date_end:
                    start_date = line.date_start.strftime('%Y-%m-%d')
                    end_date = line.date_end.strftime('%Y-%m-%d')
                    if start_date > today.strftime('%Y-%m-%d'):
                        continue
                    elif end_date > today.strftime('%Y-%m-%d'):
                        days += int((today - line.date_start) /
                                    timedelta(days=1)) + 1
                    else:
                        days += int((line.date_end - line.date_start) /
                                    timedelta(days=1)) + 1
            rec.antiquity = days

    @api.multi
    @api.onchange('calendar_ids')
    def _onchange_calendar_ids(self):
        actual_date = date.today().strftime('%Y-%m-%d')
        for rec in self:
            for line in rec.calendar_ids:
                if line.date_start and line.date_end:
                    start_date = line.date_start.strftime('%Y-%m-%d')
                    end_date = line.date_end.strftime('%Y-%m-%d')
                    if actual_date >= start_date and actual_date <= end_date:
                        rec.actual_calendar_id = line.calendar_id
                        break

    @api.model
    def _cron_refresh_actual_calendar(self):
        records = self.env['hr.employee'].search([])
        actual_date = date.today().strftime('%Y-%m-%d')

        for record in records:
            for line in record.calendar_ids:
                start_date = line.date_start.strftime('%Y-%m-%d')
                end_date = line.date_end.strftime('%Y-%m-%d')
                if actual_date >= start_date and actual_date <= end_date:
                    record.update({'actual_calendar_id': line.calendar_id})
                    break

    @api.model
    def _cron_refresh_antiquity(self):
        records = self.env['hr.employee'].search([])
        today = date.today()
        days = 0
        for rec in records:
            for line in rec.calendar_ids:
                if line.date_start and line.date_end:
                    start_date = line.date_start.strftime('%Y-%m-%d')
                    end_date = line.date_end.strftime('%Y-%m-%d')
                    if start_date > today.strftime('%Y-%m-%d'):
                        continue
                    elif end_date > today.strftime('%Y-%m-%d'):
                        days += int((today - line.date_start) /
                                    timedelta(days=1)) + 1
                    else:
                        days += int((line.date_end - line.date_start) /
                                    timedelta(days=1)) + 1
            rec.antiquity = days

    @api.model
    def _cron_year_up(self):
        records = self.env['hr.employee'].search([])

        for rec in records:
            for line in rec.calendar_ids:
                if line.date_start and line.date_end:
                    line.date_end = line.date_end + relativedelta(years=1)
                    line.date_start = line.date_start + relativedelta(years=1)

    @api.model
    def _cron_year_down(self):
        records = self.env['hr.employee'].search([])

        for rec in records:
            for line in rec.calendar_ids:
                if line.date_start and line.date_end:
                    line.date_start = line.date_start - relativedelta(years=1)
                    line.date_end = line.date_end - relativedelta(years=1)
