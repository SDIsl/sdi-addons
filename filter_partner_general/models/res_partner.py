from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone_without_blanks = fields.Char(
        compute='compute_phone_without_blanks',
        string='Phone Without Blanks',
        store=True,
    )

    @api.depends('phone', 'mobile')
    def compute_phone_without_blanks(self):
        for res in self:
            res.phone_without_blanks = ''.join((
                str(res.phone).replace(' ', ''),
                str(res.mobile).replace(' ', '')
            ))
