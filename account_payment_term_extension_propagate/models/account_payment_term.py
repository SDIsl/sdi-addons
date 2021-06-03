# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import api, exceptions, fields, models


class AccountPaymentTermHoliday(models.Model):
    _inherit = 'account.payment.term.holiday'

    propagate = fields.Boolean(
        string="Propagate",
        default=True,
        help="Checked, this date will be available next year"
    )

    def cron_propagate_holiday(self):
        for date in self.search([
            ('propagate', '=', True),
            ('holiday', '<', fields.Date.today()),
        ]):
            date.write(
                {
                    'holiday': fields.Date.to_string(
                        fields.Date.from_string(
                            date.holiday) +
                        relativedelta(
                            years=1)),
                    'date_postponed': fields.Date.to_string(
                        fields.Date.from_string(
                            date.date_postponed) +
                        relativedelta(
                            years=1))})
