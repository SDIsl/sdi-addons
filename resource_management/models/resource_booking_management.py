###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Booking(models.Model):
    _name = 'resource.booking.management'
    _description = 'Resource bookings of an employee between two datetimes.'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        (
            'check_datetimes',
            'check(start_datetime <= end_datetime)',
            'The start datetime cannot be later than the end datetime!',
        ),
    ]

    name = fields.Char(
        string='Name',
        required=True,
    )
    resource_id = fields.Many2one(
        comodel_name='product.template',
        string='Resource',
        required=True,
        domain=[('is_a_resource', '=', 1), ('is_bookable', '=', 1)],
        track_visibility='onchange',
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
        track_visibility='onchange',
        default=lambda self: self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid),
        ], limit=1),
    )
    start_datetime = fields.Datetime(
        string='Start Datetime',
        required=True,
        track_visibility='onchange',
        copy=False,
    )
    end_datetime = fields.Datetime(
        string='End Datetime',
        required=True,
        track_visibility='onchange',
        copy=False,
    )

    @api.onchange('resource_id', 'employee_id')
    def _onchange_resource_and_employee(self):
        if not self.name and self.resource_id and self.employee_id and \
             self.resource_id.name and self.employee_id.name:
            self.name = self.resource_id.name + ' - ' + self.employee_id.name

    @api.one
    @api.constrains('start_datetime', 'end_datetime', 'resource_id')
    def _check_start_end_datetimes(self):
        bookings = self.search([
            ('id', '!=', self.id),
            ('resource_id', '=', self.resource_id.id),
        ])
        for booking in bookings:
            if self.resource_id and self.start_datetime and \
                self.end_datetime and \
                not (self.start_datetime >= booking.end_datetime) and \
                    not (self.end_datetime <= booking.start_datetime):
                raise ValidationError(_('Selected resource already has a'
                                      ' booking on that datetime range.'))
