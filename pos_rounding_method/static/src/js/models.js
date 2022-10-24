odoo.define('pos_rounding_method_point_of_sale.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models')
    var round_pr = require('web.utils').round_precision;

    models.load_models({
        model: 'res.config.settings',
        fields: ['rounding_method'],
        loaded: function(self, configs) {
            self.pos_rounding_method = configs[configs.length - 1].rounding_method;
        },
    });

    models.Orderline = models.Orderline.extend({
        _map_tax_fiscal_position: function(tax) {
            var current_order = this.pos.get_order();
            var order_fiscal_position = current_order && current_order.fiscal_position;
    
            if (order_fiscal_position) {
                var mapped_tax = _.find(order_fiscal_position.fiscal_position_taxes_by_id, function (fiscal_position_tax) {
                    return fiscal_position_tax.tax_src_id[0] === tax.id;
                });
    
                if (mapped_tax) {
                    tax = this.pos.taxes_by_id[mapped_tax.tax_dest_id[0]];
                }
            }
    
            return tax;
        },
        _compute_all: function(tax, base_amount, quantity) {
            if (tax.amount_type === 'fixed') {
                var sign_base_amount = Math.sign(base_amount) || 1;
                // Since base amount has been computed with quantity
                // we take the abs of quantity
                // Same logic as bb72dea98de4dae8f59e397f232a0636411d37ce
                return tax.amount * sign_base_amount * Math.abs(quantity);
            }
            if ((tax.amount_type === 'percent' && !tax.price_include) || (tax.amount_type === 'division' && tax.price_include)){
                return base_amount * tax.amount / 100;
            }
            if (tax.amount_type === 'percent' && tax.price_include){
                return base_amount - (base_amount / (1 + tax.amount / 100));
            }
            if (tax.amount_type === 'division' && !tax.price_include) {
                return base_amount / (1 - tax.amount / 100) - base_amount;
            }
            return false;
        },
        compute_all: function (taxes, price_unit, quantity, currency_rounding, no_map_tax) {
            var self = this;
            var list_taxes = [];
            var currency_rounding_bak = currency_rounding;
            if (this.pos.pos_rounding_method === "round_globally") {
                currency_rounding = currency_rounding * 0.00001;
            }
            var total_excluded = round_pr(price_unit * quantity, currency_rounding);
            var total_included = total_excluded;
            var base = total_excluded;
            _(taxes).each(function (tax) {
                if (!no_map_tax) {
                    tax = self._map_tax_fiscal_position(tax);
                }
                if (!tax) {
                    return;
                }
                if (tax.amount_type === 'group') {
                    var ret = self.compute_all(tax.children_tax_ids, price_unit, quantity, currency_rounding);
                    total_excluded = ret.total_excluded;
                    base = ret.total_excluded;
                    total_included = ret.total_included;
                    list_taxes = list_taxes.concat(ret.taxes);
                }
                else {
                    var tax_amount = self._compute_all(tax, base, quantity);
                    tax_amount = round_pr(tax_amount, currency_rounding);

                    if (tax_amount) {
                        if (tax.price_include) {
                            total_excluded -= tax_amount;
                            base -= tax_amount;
                        }
                        else {
                            total_included += tax_amount;
                        }
                        if (tax.include_base_amount) {
                            base += tax_amount;
                        }
                        var data = {
                            id: tax.id,
                            amount: tax_amount,
                            name: tax.name,
                        };
                        list_taxes.push(data);
                    }
                }
            });
            return {
                taxes: list_taxes,
                total_excluded: round_pr(total_excluded, currency_rounding_bak),
                total_included: round_pr(total_included, currency_rounding_bak)
            };
        }
    });

    models.Order = models.Order.extend({
        get_total_tax: function () {
            if (this.pos.pos_rounding_method === "round_globally") {
                // As always, we need:
                // 1. For each tax, sum their amount across all order lines
                // 2. Round that result
                // 3. Sum all those rounded amounts
                var groupTaxes = {};
                this.orderlines.each(function (line) {
                    var taxDetails = line.get_tax_details();
                    var taxIds = Object.keys(taxDetails);
                    for (var t = 0; t < taxIds.length; t++) {
                        var taxId = taxIds[t];
                        if (!(taxId in groupTaxes)) {
                            groupTaxes[taxId] = 0;
                        }
                        groupTaxes[taxId] += taxDetails[taxId];
                    }
                });

                var sum = 0;
                var taxIds = Object.keys(groupTaxes);
                for (var j = 0; j < taxIds.length; j++) {
                    var taxAmount = groupTaxes[taxIds[j]];
                    sum += round_pr(taxAmount, this.pos.currency.rounding);
                }
                return sum;
            } else {
                return round_pr(this.orderlines.reduce((function (sum, orderLine) {
                    return sum + orderLine.get_tax();
                }), 0), this.pos.currency.rounding);
            }
        }
    });

});
