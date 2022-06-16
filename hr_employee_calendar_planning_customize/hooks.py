###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, SUPERUSER_ID
from datetime import date


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    employees = env['hr.employee'].search([])

    actual_date = date.today().strftime('%Y-%m-%d')
    for employee in employees:
        for line in employee.calendar_ids:
            if line.date_start and line.date_end:
                start_date = line.date_start.strftime('%Y-%m-%d')
                end_date = line.date_end.strftime('%Y-%m-%d')
                if actual_date >= start_date and actual_date <= end_date:
                    employee.actual_calendar_id = line.calendar_id
                    break
