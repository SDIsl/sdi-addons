from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    valued = fields.Boolean(
        related='partner_id.valued_picking', readonly=True,
    )
    currency_id = fields.Many2one(
        related='sale_id.currency_id', readonly=True,
        string='Currency',
    )

    amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
    )

    amount_total = fields.Monetary(
        string='Total',
        default=0,
    )

    @api.multi
    def _compute_amount_all(self):
        for pick in self:
            round_curr = pick.currency_id.round
            amount_tax = 0.0
            items_aux = pick.get_taxes_values()
            amount_untaxed = 0.0
            for line in pick.move_line_ids:
                amount_untaxed += round_curr(line.sale_price_subtotal)
            for tax in items_aux:
                amount_tax += round_curr(tax[1])
            pick.update({
                'amount_untaxed': amount_untaxed,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.multi
    def get_taxes_values(self):
        self.ensure_one()
        res = {}
        for line in self.move_line_ids:
            price_reduce = line.sale_price_unit - line.sale_price_unit * line.discount/100
            context = self.env.context.copy()
            context.update({"uom": line.product_uom_id})
            taxes = line.sale_line.tax_id.with_context(context).compute_all(price_reduce,
            quantity=line.qty_done*line.product_uom_id.factor_inv, product=line.product_id, partner=self.partner_id)['taxes']
            for tax in line.sale_line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                for t in taxes:
                    if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                        res[group]['amount'] += t['amount']
                        res[group]['base'] += t['base']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [(l[0].name, l[1]['amount'], l[1]['base'], len(res)) for l in res]
        return res

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        self.valued_calculation()
        return res


    @api.multi
    def valued_calculation(self):
        for picking in self:
            print(picking.id)
            if picking.sale_id:
                picking.move_line_ids._compute_sale_order_line_fields()
                picking._compute_amount_all()

    def cron_calculate(self):
        valores = self.env['stock.picking'].search([
            ('state', '=', 'done'),
            ('picking_type_id', '=', 1),
            ('amount_total', '=', 0),
            ('sale_id', '!=', False)
        ])
        for item in valores:
            item.valued_calculation()
