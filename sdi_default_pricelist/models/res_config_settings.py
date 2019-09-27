from ast import literal_eval
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Default Pricelist',
        help="Pricelist used like default.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        default_pricelist_id = literal_eval(ICPSudo.get_param(
            'sdi_default_pricelist.default_pricelist_id', default='False'))
        res.update(
            default_pricelist_id=default_pricelist_id,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        if self.default_pricelist_id:
            self.default_pricelist_id._onchange_default_pricelist()
        ICPSudo.set_param(
            "sdi_default_pricelist.default_pricelist_id",
            self.default_pricelist_id.id
        )
