###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models
from odoo.tools.float_utils import float_round


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def tbai_prepare_invoice_values(self):
        vals = super().tbai_prepare_invoice_values()
        lines = vals['tbai_invoice_line_ids']
        for line in self.invoice_global_discount_ids:
            description_line = line.name[:250]
            if (
                    self.company_id.tbai_protected_data
                    and self.company_id.tbai_protected_data_txt
            ):
                description_line = self.company_id.tbai_protected_data_txt[
                                   :250]
            taxes = line.tax_ids.compute_all(
                line.discount_amount,
                line.currency_id,
                -1)

            lines.append(
                (
                    0,
                    0,
                    {
                        "description": description_line,
                        "quantity": "-1.00",
                        "price_unit": "%.2f" % float_round(
                            line.discount_amount, 2),
                        "discount_amount": "0.00",
                        "amount_total": "%.2f" % float_round(
                            taxes['total_included'], 2),
                    },
                )
            )
        vals["tbai_invoice_line_ids"] = lines
        return vals
