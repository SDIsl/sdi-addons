###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestDisabledVATCheck(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env.user.company_id.vat_check_vies = False
        self.params = self.env['ir.config_parameter'].sudo()

    def test_vat_check_enabled(self):
        self.params.set_param(
            'partner_disable_vat_check_option.disable_vat_check', False)

        test_partner = self.env['res.partner'].create({'name': "John Dex"})

        with self.assertRaises(ValidationError):
            test_partner.write({'vat': 'BE42', 'country_id': None})

    def test_vat_check_disabled(self):
        self.params.set_param(
            'partner_disable_vat_check_option.disable_vat_check', True)

        test_partner = self.env['res.partner'].create({'name': "John Dex"})

        test_partner.write({'vat': 'BE42', 'country_id': None})
        self.assertEqual(test_partner.vat, 'BE42')
