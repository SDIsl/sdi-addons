###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    create_upsell_activity = fields.Boolean(
        string='Create Upsell Activity',
        default=True,
        config_parameter='sale_order_no_automatic_upsell_activity.'
        'create_upsell_activity',
    )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'sale_order_no_automatic_upsell_activity.create_upsell_activity',
            self.create_upsell_activity
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        create_upsell_activity = ICPSudo.get_param(
            'sale_order_no_automatic_upsell_activity.create_upsell_activity'
        )
        res.update(
            create_upsell_activity=create_upsell_activity
        )
        return res
