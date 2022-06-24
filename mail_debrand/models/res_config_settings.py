from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    linkUrl = fields.Char(string='Link to use',
                          config_parameter="mail_debrand.linkUrl")

    linkText = fields.Char(string="Text for the link",
                           config_parameter="mail_debrand.linkText")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
                'mail_debrand.linkUrl', self.linkUrl
                )
        self.env['ir.config_parameter'].set_param(
                'mail_debrand.linkText', self.linkText
                )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        urlToUse = ICPSudo.get_param('mail_debrand.linkUrl')
        textForUrl = ICPSudo.get_param('mail_debrand.linkText')

        res.update(
            linkUrl=urlToUse,
            linkText=textForUrl
        )
        return res
