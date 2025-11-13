odoo.define('l10n_es_verifactu_POS.patch_receipt_qr', function (require) {
    "use strict";

    var models  = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var rpc     = require('web.rpc');

    // Helper: maneja jQuery Deferred (v11) o Promise/thenable
    function handlePromiseLike(def, onOk, onErr) {
        if (!def) { onOk(); return; }
        if (def && typeof def.fail === 'function') {         // jQuery Deferred (Odoo 11)
            def.then(onOk).fail(onErr);
        } else if (def && typeof def.then === 'function') {  // Promise/thenable
            def.then(onOk, onErr);
        } else {
            onOk();
        }
    }

    // ---------- PATCH Order ----------
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attr, options) {
            _super_order.initialize.call(this, attr, options);
            this.qrcode           = this.qrcode || null;   // data URL
            this.verifactu_status = this.verifactu_status || null;
            this.show_qr_always   = !!this.show_qr_always; // bool
            console.log("[VF11][Order.init] uid=", this.uid, "name=", this.name,
                        "prev=", { qrcode: this.qrcode, verifactu_status: this.verifactu_status, show_qr_always: this.show_qr_always });
        },

        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.qrcode           = this.qrcode;
            json.verifactu_status = this.verifactu_status;
            json.show_qr_always   = this.show_qr_always;
            console.log("📤 [VF][Order.export_as_JSON]", {
                uid: this.uid, name: this.name,
                qrcode: !!this.qrcode, verifactu_status: this.verifactu_status, show_qr_always: this.show_qr_always
            });
            return json;
        },

        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.qrcode           = json.qrcode || null;
            this.verifactu_status = json.verifactu_status || null;
            this.show_qr_always   = !!json.show_qr_always;
            console.log("📥 [VF][Order.init_from_JSON]", json);
        },

        export_for_printing: function () {
            var json = _super_order.export_for_printing.call(this);
            json.qrcode           = this.qrcode;
            json.verifactu_status = this.verifactu_status;
            json.show_qr_always   = this.show_qr_always;
            console.log("🧾 [VF][Order.export_for_printing]", {
                uid: this.uid, name: this.name,
                qrcode: !!this.qrcode, verifactu_status: this.verifactu_status, show_qr_always: this.show_qr_always
            });
            return json;
        },
    });

    // ---------- Util: leer QR directamente de account.invoice ----------
    function fetch_qr_from_invoice_v11(order) {
        // En Odoo 11 el pos_reference suele ser order.uid; algunos setups usan order.name
        var ref_uid  = order.uid  || '';
        var ref_name = order.name || '';

        var domain = ['|',
            ['pos_reference', '=', ref_uid],
            ['pos_reference', '=', ref_name],
        ];

        console.log("[VF11][fetch] dominio=", domain);

        // 1) Obtener pos.order con invoice_id
        return rpc.query({
            model: 'pos.order',
            method: 'search_read',
            args: [domain, ['invoice_id'], 0, 1, 'id desc'],
        }).then(function (orders) {
            if (!orders || !orders.length) {
                console.warn("[VF11][fetch] pos.order no encontrado");
                return;
            }
            var po = orders[0];
            if (!po.invoice_id || !po.invoice_id.length) {
                console.warn("[VF11][fetch] pos.order sin invoice_id (aún).");
                return;
            }
            var inv_id = po.invoice_id[0];
            console.log("[VF11][fetch] invoice_id=", inv_id);

            // 2) Leer account.invoice (campos VeriFactu)
            return rpc.query({
                model: 'account.invoice',
                method: 'read',
                args: [[inv_id], ['verifactu_qr', 'verifactu_status', 'verifactu_last_numero', 'show_qr_always', 'number', 'state']],
            }).then(function (inv_recs) {
                if (!inv_recs || !inv_recs.length) {
                    console.warn("[VF11][fetch] account.invoice vacío");
                    return;
                }
                var inv = inv_recs[0];
                console.log("[VF11][fetch] factura:", inv);

                // Preferimos el QR que ya venga de la factura
                var data_url = null;
                if (inv.verifactu_qr) {
                    var b64 = inv.verifactu_qr;  // ya es base64 (Binary en Odoo)
                    data_url = "data:image/png;base64," + b64;
                    order.qrcode = data_url;
                    order.show_qr_always = true; // fuerza visualización
                    console.log("[VF11][fetch] ✅ QR copiado de factura (len base64=", (b64||"").length, ")");
                } else {
                    console.warn("[VF11][fetch] La factura no tiene verifactu_qr (aún).");
                }

                // Estado: usamos verifactu_status si llega
                order.verifactu_status = inv.verifactu_status || order.verifactu_status || null;

                // Si no hay QR pero queremos mostrar (por config), respeta flag
                if (!order.show_qr_always) {
                    order.show_qr_always = !!inv.show_qr_always;
                }

                // Log redondo de qué quedó en el order
                console.log("[VF11][fetch] asignado desde invoice →", {
                    qrcode: !!order.qrcode,
                    verifactu_status: order.verifactu_status,
                    show_qr_always: order.show_qr_always,
                    inv_number: inv.number,
                    inv_state: inv.state,
                    vf_last_numero: inv.verifactu_last_numero
                });
            });
        }, function (err) {
            console.error("[VF11][fetch] Error search_read pos.order:", err);
        });
    }

    // ---------- PATCH PaymentScreenWidget ----------
    var _super_validate = screens.PaymentScreenWidget.prototype.validate_order;
    screens.PaymentScreenWidget.include({
        validate_order: function (force_validation) {
            var self  = this;
            var order = self.pos.get_order();

            console.log("[VF11][Payment.validate] start force_validation=", force_validation,
                        "order?", !!order, "paid?", order && order.is_paid && order.is_paid(),
                        "to_invoice?", order && order.is_to_invoice && order.is_to_invoice());

            if (!order) {
                this.gui.show_popup('error', {
                    title: 'Error: orden no encontrada',
                    body: 'No se ha podido obtener la orden actual.',
                });
                return;
            }
            if (!order.is_paid()) {
                return;
            }

            order.initialize_validation_date();

            if (order.is_to_invoice && order.is_to_invoice()) {
                // Flujo con factura ya previsto por POS
                var d1 = this.pos.push_and_invoice_order(order);
                handlePromiseLike(d1, function () {
                    console.log("[VF11][Payment.validate] push_and_invoice OK → leer invoice");
                    var d2 = fetch_qr_from_invoice_v11(order);
                    handlePromiseLike(d2, function () {
                        console.log("[VF11][Payment.validate] fetch invoice OK → finalize");
                        _super_validate.call(self, force_validation);
                    }, function (e2) {
                        console.error("[VF11][Payment.validate] fetch invoice ERROR:", e2);
                        _super_validate.call(self, force_validation);
                    });
                }, function (err) {
                    console.error("[VF11][Payment.validate] push_and_invoice_order ERROR:", err);
                    self.gui.show_popup('error', {
                        title: 'Error de facturación',
                        body: (err && err.message) || 'No se pudo facturar el ticket.',
                    });
                });
            } else {
                // Flujo “ticket” → tras guardar, intentamos leer invoice_id en pos.order y luego invoice
                var d3 = this.pos.push_order(order);
                handlePromiseLike(d3, function () {
                    console.log("[VF11][Payment.validate] push_order OK → leer invoice");
                    var d4 = fetch_qr_from_invoice_v11(order);
                    handlePromiseLike(d4, function () {
                        console.log("[VF11][Payment.validate] fetch invoice OK → finalize");
                        _super_validate.call(self, force_validation);
                    }, function (e4) {
                        console.error("[VF11][Payment.validate] fetch invoice ERROR:", e4);
                        _super_validate.call(self, force_validation);
                    });
                }, function (err) {
                    console.error("[VF11][Payment.validate] push_order ERROR:", err);
                    self.gui.show_popup('error', {
                        title: 'Error al enviar el pedido',
                        body: (err && err.message) || 'No se pudo enviar el pedido.',
                    });
                });
            }
        },
    });
});
