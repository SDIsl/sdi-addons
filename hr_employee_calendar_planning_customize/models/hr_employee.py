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
        default=0,
    )
    antiquity_years = fields.Char(
        string='Years',
        compute='_compute_antiquity',
        store=True,
    )

    contract_start = fields.Date(
        string='Fecha de contratación',
        copy=False,
    )
    contract_end = fields.Date(
        string='Fecha salida',
    )

    tenure = fields.Integer(
        string='Antigüedad (Dias)',
        compute='_compute_tenure',
        store=True,
        depends=['contract_start', 'contract_end'],
    )
    tenure_char = fields.Char(
        string="Antigüedad en la empresa",
        compute='_show_tenure'
    )

    @api.depends(
        'calendar_ids', 'calendar_ids.date_start', 'calendar_ids.date_end'
    )
    def _compute_antiquity(self):
        today = date.today()

        for rec in self:
            days = 0
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

            years = days // 365
            days = days % 365

            rec.antiquity = days
            if not years and not days:
                rec.antiquity_years = False
            else:
                if len(str(years)) == 1:
                    rec.antiquity_years = '0' + str(years)
                else:
                    rec.antiquity_years = str(years)

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
                if start_date <= actual_date <= end_date:
                    record.update({'actual_calendar_id': line.calendar_id})
                    break

    @api.model
    def _cron_refresh_antiquity(self):
        records = self.env['hr.employee'].search([])
        today = date.today()

        for rec in records:
            days = 0
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

            years = days // 365
            days = days % 365

            rec.antiquity = days
            if not years and not days:
                rec.antiquity_years = False
            else:
                if len(str(years)) == 1:
                    rec.antiquity_years = '0' + str(years)
                else:
                    rec.antiquity_years = str(years)

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

    def _compute_inicio_contrato(self):
        for rec in self.filtered(lambda a: a.calendar_ids):
            inicio = min(rec.calendar_ids.mapped('date_start')) or False
            rec.contract_start = inicio

    @api.depends('contract_start', 'contract_end')
    def _compute_tenure(self):
        for rec in self.filtered(lambda x: x.contract_start):
            fin = rec.contract_end or date.today()
            rec.tenure = (fin - rec.contract_start).days

    def _show_tenure(self):
        for rec in self:
            y = str(rec.tenure // 365).zfill(2)
            m = str((rec.tenure % 365) // 30).zfill(2)
            d = str((rec.tenure % 365) % 30).zfill(2)
            rec.tenure_char = "{} años, {} meses, {} días.".format(y, m, d)
