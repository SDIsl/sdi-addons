from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warning_message = fields.Char(
        string='Warning message to show',
        config_parameter='project_exceeded_time_warning_banner.warning_message'
        )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'project_exceeded_time_warning_banner.warning_message',
            self.warning_message
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        messageToUSe = ICPSudo.get_param(
            'project_exceeded_time_warning_banner.warning_message'
            )

        res.update(
            warning_message=messageToUSe
        )
        return res
