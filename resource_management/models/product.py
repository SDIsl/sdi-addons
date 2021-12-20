###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models


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
        track_visibility='onchange',
    )
    default_code = fields.Char(
        track_visibility='onchange',
    )
    quantity = fields.Integer(
        string='Quantity',
        default=1,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        track_visibility='onchange',
    )
    booking_ids = fields.One2many(
        comodel_name='resource.booking.management',
        inverse_name='resource_id',
        string='Bookings',
        domain=lambda self: [('end_datetime', '>', fields.datetime.now())],
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

    @api.multi
    def write(self, vals):
        for resource in self:
            msg = _('<p><span class="fa fa-pencil" title="Edited"/> Resource '
                    '<strong>{resource}</strong> has been modified:</br>'
                    ).format(resource=resource.name,)
            post = False
            if 'employee_id' in vals:
                employee = resource.env['hr.employee'].browse(
                    vals['employee_id']
                )
                if employee != resource.employee_id:
                    msg += _('<li><strong>Employee:</strong> {old_val} '
                             '<span class="fa fa-long-arrow-right"'
                             ' title="Changed"/> {new_val}</li>').format(
                        old_val=resource.employee_id.name,
                        new_val=employee.name,
                    )
                    post = True
            msg += '</p>'
            if post:
                resource.employee_id.message_post(body=msg)
                employee.message_post(body=msg)
        return super().write(vals)
