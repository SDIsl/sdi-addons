###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################

from odoo import fields, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    control_digit = fields.Selection(
        selection=[
            ('10', "Mod 10")
        ],
        string='Control digit method',
    )

    def _next_do(self):
        res = super(IrSequence, self)._next_do()
        if self.control_digit == '10':
            checksum = 0
            for i, digit in enumerate(reversed(res)):
                checksum += int(digit) * 3 if (i % 2 == 0) else int(digit)
            res = '%s%d' % (res, (10 - (checksum % 10)) % 10)
        return res
