###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('facturae', 'vat', 'state_id', 'country_id', 'street')
    def check_facturae(self):
        for record in self:
            if record.facturae:
                if not record.vat:
                    raise ValidationError(
                        _('Vat must be defined for factura-e enabled partners.')
                    )
                if not record.street:
                    raise ValidationError(
                        _('Street must be defined for factura-e enabled partners.')
                    )
                if not record.country_id:
                    raise ValidationError(
                        _('Country must be defined for factura-e enabled partners.')
                    )
                if record.country_id.code_alpha3 == 'ESP':
                    if not record.state_id:
                        raise ValidationError(
                            _('State must be defined for factura-e enabled partners.')
                        )
