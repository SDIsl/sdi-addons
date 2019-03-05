# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class Stage(models.Model):
    _inherit = "crm.stage"

    attachment = fields.Boolean('Attachment',
                                help=_('This stage require a attachment.'))
    revenue = fields.Boolean('Expected Revenue',
                                help=_('This stage requires to expected revenue.'))
    deadline = fields.Boolean('Date deadline',
                                help=_('This stage requires to have date deadline.'))
    tags = fields.Boolean('Tags',
                          help=_('This stage requires to have tags.'))
    notification = fields.Boolean('Notification',
                          help=_('This stage send notification.'))
    responsible = fields.Many2one('res.users', string='Responsible', index=True)

    @api.onchange('notification')
    def _onchange_notification(self):
        for state in self:
            if not state.notification:
                state.responsible = None
