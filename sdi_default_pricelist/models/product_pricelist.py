from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.onchange('sequence')
    def _onchange_default_pricelist(self):
        pricelist_id_id = self.env['ir.config_parameter'].sudo().get_param(
            'sdi_default_pricelist.default_pricelist_id')
        pricelist_id = self.browse(int(pricelist_id_id))
        if pricelist_id.exists() and pricelist_id.sequence != 0:
            pricelist = self.search([('active', '=', 'True')])
            f = 1
            for rate in pricelist:
                rate.sequence = f
                f += 1
            pricelist_id.sequence = 0
