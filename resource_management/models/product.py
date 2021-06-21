###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, fields, models
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_a_resource = fields.Boolean(
        string='Is a resource',
    )
    is_bookable = fields.Boolean(
        string='Is bookable',
    )
    expiration_date = fields.Date(
        string='Expiration date',
    )
    quantity = fields.Integer(
        string="Quantity",
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
    )
    booking_ids = fields.One2many(
        comodel_name='resource.booking.management',
        inverse_name='resource_id',
        string='Bookings',
        domain=[('end_datetime', '>', datetime.now())],
    )

    def button_resource_bookings(self):
        tree_view = self.env.ref(
            'resource_management.resource_booking_management_view_tree')
        calendar_view = self.env.ref(
            'resource_management.resource_booking_management_view_calendar')
        form_view = self.env.ref(
            'resource_management.'
            'resource_booking_management_view_form_from_resource')
        return{
            'name': _('Bookings'),
            'view_mode': 'tree,calendar,form',
            'res_model': 'resource.booking.management',
            'type': 'ir.actions.act_window',
            'views': [(tree_view.id, 'tree'), (calendar_view.id, 'calendar'),
                      (form_view.id, 'form')],
            'domain': [('resource_id', '=', self.id)],
            'context': {'default_resource_id': self.id},
        }
