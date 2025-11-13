odoo.define('l10n_es_verifactu_POS.pos_qr_patch', function (require) {
    "use strict";

    var models  = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var rpc     = require('web.rpc');

    // ------------------------------------------------------------
    // Helper: maneja Promise nativo, jQuery Deferred o undefined (v11)
    // ------------------------------------------------------------
    function handlePromiseLike(def, onOk, onErr) {
        if (!def) {
            console.log("[VF][helper] def=undefined → onOk()");
            try { onOk(); } catch (e) { console.error("[VF][helper] onOk threw:", e); }
            return;
        }
        if (def && typeof def.fail === 'function') {
            console.log("[VF][helper] jQuery Deferred detectado");
            def.then(function (r) {
                try { onOk(r); } catch (e) { console.error("[VF][helper] onOk threw:", e); }
            }).fail(function (err) {
                try { onErr(err); } catch (e) { console.error("[VF][helper] onErr threw:", e); }
            });
            return;
        }
        if (def && typeof def.then === 'function') {
            console.log("[VF][helper] thenable/Promise detectado");
            def.then(function (r) {
                try { onOk(r); } catch (e) { console.error("[VF][helper] onOk threw:", e); }
            }, function (err) {
                try { onErr(err); } catch (e) { console.error("[VF][helper] onErr threw:", e); }
            });
            return;
        }
        console.log("[VF][helper] def no es thenable → onOk()");
        try { onOk(); } catch (e) { console.error("[VF][helper] onOk threw:", e); }
    }

    // ------------------------------------------------------------
    // PATCH Order
    // ------------------------------------------------------------
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attr, options) {
            _super_order.initialize.call(this, attr, options);
            var prev = {
                qrcode: this.qrcode,
                verifactu_status: this.verifactu_status,
                show_qr_always: this.show_qr_always,
            };
            this.qrcode           = this.qrcode || null;
            this.verifactu_status = this.verifactu_status || null;
            this.show_qr_always   = this.show_qr_always || false;

            console.log("[VF][Order.init] uid=", this.uid, "name=", this.name,
                "prev=", prev, "now=",
                { qrcode:this.qrcode, verifactu_status:this.verifactu_status, show_qr_always:this.show_qr_always });
        },

        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.qrcode           = this.qrcode;
            json.verifactu_status = this.verifactu_status;
            json.show_qr_always   = this.show_qr_always;
            console.log("📤 [VF][Order.export_as_JSON]",
                { uid:this.uid, name:this.name, qrcode: !!this.qrcode, verifactu_status:this.verifactu_status, show_qr_always:this.show_qr_always });
            return json;
        },

        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.qrcode           = json.qrcode;
            this.verifactu_status = json.verifactu_status;
            this.show_qr_always   = json.show_qr_always;
            console.log("📥 [VF][Order.init_from_JSON]",
                { uid:this.uid, name:this.name, qrcode: !!this.qrcode, verifactu_status:this.verifactu_status, show_qr_always:this.show_qr_always });
        },

        export_for_printing: function () {
            var json = _super_order.export_for_printing.call(this);
            json.qrcode           = this.qrcode;
            json.verifactu_status = this.verifactu_status;
            json.show_qr_always   = this.show_qr_always;
            console.log("🧾 [VF][Order.export_for_printing]",
                { uid:this.uid, name:this.name, qrcode: !!this.qrcode, verifactu_status:this.verifactu_status, show_qr_always:this.show_qr_always });
            return json;
        },
    });

    // ------------------------------------------------------------
    // FETCH desde pos.order (siempre leemos cache persistente)
    // ------------------------------------------------------------
    function fetch_pos_verifactu_fields(order) {
        // En v11 pos_reference acostumbra a ser order.uid; en otras, order.name
        var ref_uid  = order.uid  || '';
        var ref_name = order.name || '';

        var domain = ['|',
            ['pos_reference', '=', ref_uid],
            ['pos_reference', '=', ref_name],
        ];

        var fields_list = ['qrcode', 'verifactu_status_pos', 'show_qr_always_pos'];

        console.log("[VF][fetch] dominio=", domain, "fields=", fields_list);

        // search_read(domain, fields, offset=0, limit=1, order='id desc') → POSICIONALES (v11)
        return rpc.query({
            model: 'pos.order',
            method: 'search_read',
            args: [domain, fields_list, 0, 1, 'id desc'],
        }).then(function (orders) {
            console.log("[VF][fetch] respuesta =", orders);
            if (orders && orders.length) {
                var rec = orders[0];
                var before = {
                    qrcode: order.qrcode,
                    verifactu_status: order.verifactu_status,
                    show_qr_always: order.show_qr_always,
                };
                order.qrcode           = rec.qrcode || null; // data URL si existe
                order.verifactu_status = rec.verifactu_status_pos || null;
                order.show_qr_always   = !!rec.show_qr_always_pos;
                console.log("[VF][fetch] asignado desde cache POS:",
                    "before=", before,
                    "after=", { qrcode: !!order.qrcode, verifactu_status: order.verifactu_status, show_qr_always: order.show_qr_always });
            } else {
                console.warn("[VF][fetch] pos.order no encontrado por dominio:", domain);
            }
        }, function (err) {
            console.error("[VF][fetch] Error leyendo pos.order:", err);
        });
    }

    // ------------------------------------------------------------
    // PATCH PaymentScreenWidget
    // ------------------------------------------------------------
    var _super_finalize = screens.PaymentScreenWidget.prototype.validate_order;
    screens.PaymentScreenWidget.include({
        validate_order: function (force_validation) {
            var self  = this;
            var order = self.pos.get_order();

            console.log("[VF][Payment.validate] start force_validation=", force_validation,
                "order?", !!order, "paid?", order && order.is_paid && order.is_paid());

            if (!order) {
                this.gui.show_popup('error', {
                    title: 'Error: orden no encontrada',
                    body: 'No se ha podido obtener la orden actual.',
                });
                return;
            }
            if (!order.is_paid()) {
                console.log("[VF][Payment.validate] order no está pagado → retorno");
                return;
            }

            order.initialize_validation_date();

            if (order.is_to_invoice && order.is_to_invoice()) {
                console.log("[VF][Payment.validate] Flujo con factura → push_and_invoice_order()");
                var def = this.pos.push_and_invoice_order(order);
                handlePromiseLike(def, function () {
                    console.log("[VF][Payment.validate] push_and_invoice_order OK → fetch cache POS");
                    var d2 = fetch_pos_verifactu_fields(order);
                    handlePromiseLike(d2, function () {
                        console.log("[VF][Payment.validate] fetch OK → _super_finalize()");
                        _super_finalize.call(self, force_validation);
                    }, function (err) {
                        console.error("[VF][Payment.validate] fetch ERROR (invoiced):", err, "→ _super_finalize()");
                        _super_finalize.call(self, force_validation);
                    });
                }, function (error) {
                    console.error("[VF][Payment.validate] push_and_invoice_order ERROR:", error);
                    self.gui.show_popup('error', {
                        title: 'Error de facturación',
                        body: (error && error.message) || 'No se pudo facturar el ticket.',
                    });
                });
            } else {
                console.log("[VF][Payment.validate] Flujo sin factura → push_order()");
                var def2 = this.pos.push_order(order);
                handlePromiseLike(def2, function () {
                    console.log("[VF][Payment.validate] push_order OK → fetch cache POS");
                    var d3 = fetch_pos_verifactu_fields(order);
                    handlePromiseLike(d3, function () {
                        console.log("[VF][Payment.validate] fetch OK → _super_finalize()");
                        _super_finalize.call(self, force_validation);
                    }, function (err) {
                        console.error("[VF][Payment.validate] fetch ERROR (no invoiced):", err, "→ _super_finalize()");
                        _super_finalize.call(self, force_validation);
                    });
                }, function (error) {
                    console.error("[VF][Payment.validate] push_order ERROR:", error);
                    self.gui.show_popup('error', {
                        title: 'Error al enviar el pedido',
                        body: (error && error.message) || 'No se pudo enviar el pedido.',
                    });
                });
            }
        },
    });
});
