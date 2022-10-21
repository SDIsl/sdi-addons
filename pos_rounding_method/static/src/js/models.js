odoo.define('pos_ronding_method_point_of_sale.models', function (require) {
    "use strict";

    var core = require('web.core');
    var utils = require('web.utils');
    var pos_models = require('point_of_sale.models')

    var _t = core._t;
    var round_pr = utils.round_precision;

    models.load_models(
        [
            {
                model: 'res.company',
                fields: ['currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id', 'country_id'],
                ids: function (self) { return [self.user.company_id[0]]; },
                loaded: function (self, companies) { self.company = companies[0]; },
            }, {
                model: 'pos.config',
                fields: ['rounding_method'],
                domain: function (self) { return [['id', '=', self.pos_session.config_id[0]]]; },
                loaded: function (self, configs) {
                    self.config = configs[0];
                    self.config.use_proxy = self.config.iface_payment_terminal ||
                        self.config.iface_electronic_scale ||
                        self.config.iface_print_via_proxy ||
                        self.config.iface_scan_via_proxy ||
                        self.config.iface_cashdrawer ||
                        self.config.iface_customer_facing_display;

                    if (self.config.company_id[0] !== self.user.company_id[0]) {
                        throw new Error(_t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
                    }

                    self.db.set_uuid(self.config.uuid);
                    self.set_cashier(self.get_cashier());
                    // We need to do it here, since only then the local storage has the correct uuid
                    self.db.save('pos_session_id', self.pos_session.id);

                    var orders = self.db.get_orders();
                    for (var i = 0; i < orders.length; i++) {
                        self.pos_session.sequence_number = Math.max(self.pos_session.sequence_number, orders[i].data.sequence_number + 1);
                    }
                },
            },
        ],
        { 'after': 'pos.config' }
    );

    pos_models.OrderLine = pos_models.OrderLine.extend({
        compute_all: function (taxes, price_unit, quantity, currency_rounding, no_map_tax) {
            var self = this;
            var list_taxes = [];
            var currency_rounding_bak = currency_rounding;
            if (this.pos.config.rounding_method == "round_globally") {
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

    pos_models.Order = pos_models.Order.extend({
        get_total_tax: function () {
            if (this.pos.config.rounding_method === "round_globally") {
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
