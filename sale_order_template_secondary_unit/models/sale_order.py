###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models
from datetime import timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        if not self.sale_order_template_id:
            self.require_signature = self._get_default_require_signature()
            self.require_payment = self._get_default_require_payment()
            return
        template = self.sale_order_template_id.with_context(
            lang=self.partner_id.lang)

        order_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)
            if line.product_id:
                discount = 0
                if self.pricelist_id:
                    price = self.pricelist_id.with_context(
                        uom=line.product_uom_id.id
                    ).get_product_price(line.product_id, 1, False)
                    if self.pricelist_id.discount_policy == \
                            'without_discount' and line.price_unit:
                        discount = \
                            (line.price_unit - price) / line.price_unit * 100
                        if discount < 0:
                            discount = 0
                        else:
                            price = line.price_unit

                else:
                    price = line.price_unit

                data.update({
                    'price_unit': price,
                    'discount': 100 - ((100 - discount) *
                            (100 - line.discount) / 100),
                    'product_uom_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'customer_lead': self._get_customer_lead(
                        line.product_id.product_tmpl_id),
                })
                if line.secondary_uom_id:
                    data.update({
                        'secondary_uom_qty': line.secondary_uom_qty,
                        'secondary_uom_id': line.secondary_uom_id.id,
                    })
                if self.pricelist_id:
                    data.update(
                        self.env['sale.order.line']._get_purchase_price(
                            self.pricelist_id,
                            line.product_id,
                            line.product_uom_id,
                            fields.Date.context_today(self)
                        )
                    )
            order_lines.append((0, 0, data))

        self.order_line = order_lines
        self.order_line._compute_tax_id()

        option_lines = []
        for option in template.sale_order_template_option_ids:
            data = self._compute_option_data_for_template_change(option)
            option_lines.append((0, 0, data))
        self.sale_order_option_ids = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.context_today(self) + \
                timedelta(template.number_of_days)

        self.require_signature = template.require_signature
        self.require_payment = template.require_payment

        if template.note:
            self.note = template.note
