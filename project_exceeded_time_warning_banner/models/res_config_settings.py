from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warningMessage = fields.Char(
        string='Warning message to show',
        config_parameter='project_exceeded_time_warning_banner.warningMessage'
        )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'project_exceeded_time_warning_banner.warningMessage',
            self.warningMessage
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        messageToUSe = ICPSudo.get_param(
            'project_exceeded_time_warning_banner.warningMessage'
            )

        res.update(
            warningMessage=messageToUSe
        )
        return res
