###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, fields, models
from datetime import datetime


class Employee(models.Model):
    _inherit = 'hr.employee'

    resource_ids = fields.One2many(
        comodel_name='product.template',
        inverse_name='employee_id',
        string='Resources',
    )
    booking_ids = fields.One2many(
        comodel_name='resource.booking.management',
        inverse_name='employee_id',
        string='Bookings',
        domain=[('end_datetime', '>', datetime.now())],
    )
    expendable_resource_ids = fields.One2many(
        comodel_name='resource.expendable',
        inverse_name='employee_id',
        string='Expendable Resources',
    )

    def button_employee_bookings(self):
        tree_view = self.env.ref(
            'resource_management.resource_booking_management_view_tree')
        calendar_view = self.env.ref(
            'resource_management.resource_booking_management_view_calendar')
        form_view = self.env.ref(
            'resource_management.'
            'resource_booking_management_view_form_from_employee')
        return{
            'name': _('Bookings'),
            'view_mode': 'tree,calendar,form',
            'res_model': 'resource.booking.management',
            'type': 'ir.actions.act_window',
            'views': [(tree_view.id, 'tree'), (calendar_view.id, 'calendar'),
                      (form_view.id, 'form')],
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
