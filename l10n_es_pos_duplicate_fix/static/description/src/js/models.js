odoo.define('l10n_es_pos_duplicate_fix.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields('pos.config', ['l10n_es_last_pos_order']);

    var pos_super = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        after_load_server_data: function () {
            var self = this;
            var orders = this.db.get_orders();
            var resIndex = orders.findIndex((p) => p.data.name == this.config.l10n_es_last_pos_order);
            orders.slice(0, resIndex + 1).forEach(o => self.db.remove_order(o.id));
            return pos_super.after_load_server_data.call(this);
        },
        get_simple_inv_next_number: function () {
            return this.config.l10n_es_simplified_invoice_prefix + this.get_padding_simple_inv(this.config.l10n_es_simplified_invoice_number);
        },
        push_order: function (order, opts) {
            if (order && order.simplified_invoice && this.pushed_simple_invoices.indexOf(order.simplified_invoice) === -1) {
                this.pushed_simple_invoices.push(order.simplified_invoice);
                ++this.config.l10n_es_simplified_invoice_number;
            }
            return pos_super.push_order.apply(this, arguments);
        },
    });

});
