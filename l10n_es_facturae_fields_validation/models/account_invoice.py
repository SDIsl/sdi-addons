###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def validate_facturae_fields(self):
        if not self.facturae:
            raise ValidationError(
                _(
                    'You can only create the facturae file if the client have the '
                    'facturae feature activated.'
                )
            )
        if self.state not in self._get_valid_invoice_statuses():
            raise ValidationError(
                _(
                    'You can only create Facturae files for '
                    'moves that have been validated.'
                )
            )
        if not self.partner_id.vat:
            raise ValidationError(_('Partner vat not provided'))
        if not self.partner_id.street:
            raise ValidationError(_('Partner street address is not provided'))
        if len(self.partner_id.vat) < 3:
            raise ValidationError(_('Partner vat is too small'))
        if not self.partner_id.state_id:
            raise ValidationError(_('Partner state not provided'))
        if not self.payment_mode_id:
            raise ValidationError(_('Payment mode is required'))
        if self.payment_mode_id.facturae_code:
            partner_bank = self.partner_banks_to_show()[:1]
            if (
                partner_bank
                and partner_bank.bank_id.bic
                and len(partner_bank.bank_id.bic) != 11
            ):
                raise ValidationError(_('Selected account BIC must be 11'))
            if partner_bank and len(partner_bank.acc_number) < 5:
                raise ValidationError(_('Selected account is too small'))
        self.validate_company_facturae_fields(self.company_id)
        return

    def validate_company_facturae_fields(self, company_id):
        if not company_id.partner_id.vat:
            raise ValidationError(_('Company vat not provided'))
        if not company_id.partner_id.street:
            raise ValidationError(_('Company street not provided'))
        if not company_id.partner_id.city:
            raise ValidationError(_('Company city not provided'))
        if not company_id.partner_id.state_id:
            raise ValidationError(_('Company state not provided'))
        if not company_id.partner_id.country_id:
            raise ValidationError(_('Company country not provided'))
        if not company_id.partner_id.zip:
            raise ValidationError(_('Company zip not provided'))
        if len(company_id.vat) < 3:
            raise ValidationError(_('Company vat is too small'))
        return
