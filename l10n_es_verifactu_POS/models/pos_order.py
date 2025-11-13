# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging, time
from base64 import b64encode

from ..verifactu.services.qr_content import VerifactuQRContentGenerator
# Fallback de recálculo explícito (cuando no hay métodos en el modelo)
from ..verifactu.services.hash_calculator import VerifactuHashCalculator

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # -----------------------
    # Campos POS
    # -----------------------
    qrcode = fields.Text(string="VeriFactu QR", readonly=True)
    qrcode_binary = fields.Binary("QR VeriFactu", attachment=False)

    # Bridge (no almacenados)
    verifactu_status = fields.Char(string='Estado VeriFactu', compute='_compute_verifactu_bridge', store=False)
    show_qr_always = fields.Boolean(string='Mostrar QR siempre', compute='_compute_verifactu_bridge', store=False)

    # Cache persistente para el POS
    verifactu_status_pos = fields.Char(string='VF Status (cache)', index=True)
    show_qr_always_pos = fields.Boolean(string='Mostrar QR (cache)', default=False, index=True)

    # Idempotencia
    vf_processed = fields.Boolean(string='VF procesado', default=False, index=True)
    vf_last_attempt = fields.Datetime(string='VF último intento')

    # -----------------------
    # Compat / helpers
    # -----------------------
    @api.model
    def _is_new_accounting(self):
        return bool(self.env.registry.get('account.move'))

    @staticmethod
    def _field_exists(rec, name):
        return name in getattr(rec, '_fields', {})

    @staticmethod
    def _safe_write(rec, vals):
        safe = {k: v for k, v in vals.items() if k in getattr(rec, '_fields', {})}
        if safe:
            rec.write(safe)

    def _get_invoice(self):
        self.ensure_one()
        inv = False
        if hasattr(self, 'account_move') and self.account_move:
            inv = self.account_move
        elif hasattr(self, 'invoice_id') and self.invoice_id:
            inv = self.invoice_id
        _logger.debug("[VF][compat] _get_invoice → has=%s model=%s id=%s name=%s number=%s state=%s",
                      bool(inv), getattr(inv, '_name', None), getattr(inv, 'id', None),
                      getattr(inv, 'name', None), getattr(inv, 'number', None), getattr(inv, 'state', None))
        return inv

    def _invoice_is_posted(self, inv):
        st = getattr(inv, 'state', None)
        if inv._name == 'account.move':
            return st == 'posted'
        return st in ('open', 'paid')  # v11 account.invoice

    # --- número visible por modelo ---
    @staticmethod
    def get_invoice_display_number(inv):
        """
        account.move (backport v11): usar inv.name
        account.invoice (v11/v12): usar inv.number; fallback move_name/name
        """
        if inv._name == 'account.move':
            return (getattr(inv, 'name', '') or '').strip()
        val = (getattr(inv, 'number', '') or '').strip()
        if val:
            return val
        val = (getattr(inv, 'move_name', '') or getattr(inv, 'name', '') or '').strip()
        return val

    @staticmethod
    def _is_alias_number(raw):
        raw = (raw or '').strip()
        if not raw or raw == '/':
            return True
        head = raw.split('/')[0].upper()
        return head in ('MAIN', 'POS', 'TPV', 'DRAFT')

    def _invoice_has_definitive_number(self, inv):
        raw = self.get_invoice_display_number(inv)
        return not self._is_alias_number(raw)

    def _set_invoice_date_if_needed(self, inv):
        try:
            if getattr(inv, 'state', None) == 'draft':
                if hasattr(inv, 'invoice_date') and not inv.invoice_date:
                    inv.invoice_date = fields.Date.context_today(inv)
                    _logger.info("[VF] Fijada invoice_date=%s", inv.invoice_date)
                elif hasattr(inv, 'date_invoice') and not inv.date_invoice:
                    inv.date_invoice = fields.Date.context_today(inv)
                    _logger.info("[VF] Fijada date_invoice=%s", inv.date_invoice)
        except Exception as e:
            _logger.warning("[VF] No se pudo fijar fecha factura: %s", repr(e))

    def _post_invoice_if_needed(self, inv):
        try:
            if getattr(inv, 'state', None) == 'draft':
                if hasattr(inv, 'action_post'):
                    inv.with_context(vf_skip_auto_rehash=True).action_post()
                    _logger.info("[VF] action_post (account.move)")
                elif hasattr(inv, 'action_invoice_open'):
                    inv.with_context(vf_skip_auto_rehash=True).action_invoice_open()
                    _logger.info("[VF] action_invoice_open (account.invoice)")
        except Exception as e:
            _logger.warning("[VF] No se pudo validar la factura: %s", repr(e))

    def _force_recompute_verifactu_hash(self, inv, config=None):
        """
        1) Intentar métodos del modelo (si existen).
        2) Si no existen → FALLBACK consistente: usar VerifactuHashCalculator para recalcular
           AHORA (con número definitivo ya asignado) y escribir campos si existen.
        """
        try:
            ctx = dict(self.env.context or {})
            ctx.update({'vf_force_now': True, 'vf_skip_auto_rehash': False})
            if hasattr(inv, 'verifactu_recompute_hash'):
                _logger.info("[VF] Recalculando hash con verifactu_recompute_hash(force_recalculate=True)")
                inv.with_context(ctx).verifactu_recompute_hash(force_recalculate=True)
                return True
            if hasattr(inv, 'compute_verifactu_hash'):
                _logger.info("[VF] Recalculando hash con compute_verifactu_hash()")
                inv.with_context(ctx).compute_verifactu_hash()
                return True
            if hasattr(inv, '_compute_verifactu_hash'):
                _logger.info("[VF] Recalculando hash con _compute_verifactu_hash()")
                inv.with_context(ctx)._compute_verifactu_hash()
                return True

            # ---- FALLBACK explícito ----
            _logger.warning("[VF] No hay método explícito de recálculo en %s → uso VerifactuHashCalculator.", inv._name)
            try:
                hc = VerifactuHashCalculator(invoice=inv, config=config)
                new_hash = hc.compute_and_update(force_recalculate=True)
                # compute_and_update ya hace write('verifactu_hash') si existe; invalidamos caches seguros
                self._invalidate_existing_fields(inv, 'verifactu_hash', 'verifactu_previous_hash', 'verifactu_status')
                _logger.info("[VF] Fallback de hash aplicado. New hash (prefix): %s", (new_hash or '')[:16])
                return True
            except Exception as e2:
                _logger.error("[VF] Fallback VerifactuHashCalculator ha fallado: %s", repr(e2))
                return False

        except Exception as e:
            _logger.error("[VF] Error forzando recálculo de hash: %s", repr(e))
            return False

    # --- util: invalidar solo campos existentes ---
    @staticmethod
    def _invalidate_existing_fields(inv, *fnames):
        existing = [n for n in fnames if n in getattr(inv, '_fields', {})]
        if existing:
            inv.invalidate_cache(existing)
            _logger.debug("[VF] invalidate_cache(%s) en model=%s", existing, inv._name)
        else:
            _logger.debug("[VF] invalidate_cache omitido; ninguno de %s existe en model=%s", fnames, inv._name)

    # --- ESPERA NÚMERO DEFINITIVO (robusto v11 backport) ---
    def _wait_definitive_number(self, inv, tries=14, sleep_secs=0.06):
        """
        Espera corta a que el número fiscal definitivo esté disponible.
        Evita invalidar campos inexistentes (p.ej. 'number' en account.move v11).
        """
        fields_to_invalidate = ['state']
        if self._field_exists(inv, 'name'):
            fields_to_invalidate.append('name')
        if self._field_exists(inv, 'number'):
            fields_to_invalidate.append('number')

        for i in range(int(tries)):
            if fields_to_invalidate:
                inv.invalidate_cache(fields_to_invalidate)
            current = self.get_invoice_display_number(inv)
            _logger.debug("[VF] Espera num.def. intento=%d → display=%r (model=%s invalidate=%s)",
                          i + 1, current, inv._name, fields_to_invalidate)
            if not self._is_alias_number(current):
                _logger.info("[VF] Número definitivo detectado tras %d intentos: %s", i + 1, current)
                return True, current
            time.sleep(sleep_secs)

        last = self.get_invoice_display_number(inv)
        _logger.warning("[VF] Número definitivo no disponible tras espera. display=%s state=%s",
                        last, getattr(inv, 'state', None))
        return False, last

    # -----------------------
    # Helpers de configuración VF (fuente de verdad)
    # -----------------------
    def _get_config_for_invoice(self, inv):
        """Config de VeriFactu para la compañía de la factura (v11 seguro)."""
        Config = self.env['verifactu.endpoint.config'].sudo()
        company_id = getattr(getattr(inv, 'company_id', None), 'id', False) or self.env.user.company_id.id
        rec = Config.search([('company_id', '=', company_id)], limit=1)
        return rec or Config.get_singleton_record()

    def _is_verifactu_active_from_config(self, config):
        try:
            mode_on = bool(getattr(config, 'verifactu_mode_enabled', False))
            endpoint = bool((getattr(config, 'endpoint_url', '') or '').strip())
            return mode_on and endpoint
        except Exception:
            return False

    def _should_send_now(self, inv, config):
        try:
            if hasattr(inv, 'should_send_to_verifactu') and callable(inv.should_send_to_verifactu):
                return bool(inv.should_send_to_verifactu(config))
        except Exception:
            pass
        return self._is_verifactu_active_from_config(config)

    # -----------------------
    # Compute bridge
    # -----------------------
    def _compute_verifactu_bridge(self):
        for order in self:
            inv = order._get_invoice()
            status = show = False
            if inv:
                status = getattr(inv, 'verifactu_status', False)
                show = bool(getattr(inv, 'show_qr_always', False))
            order.verifactu_status = status or False
            order.show_qr_always = show

    # -----------------------
    # Flujo POS
    # -----------------------
    @api.model
    def create_from_ui(self, orders, draft=False):
        _logger.info("[VF][POS] create_from_ui: pedidos=%d draft=%s", len(orders or []), draft)

        # A) Forzar facturación v11
        for o in (orders or []):
            data = o.get('data') or {}
            data['to_invoice'] = True
            o['data'] = data

        parent = super(PosOrder, self)
        try:
            created_orders_data = parent.create_from_ui(orders, draft)  # v11+
        except TypeError:
            created_orders_data = parent.create_from_ui(orders)         # v10

        # B) IDs creados
        created_ids = []
        for od in (created_orders_data or []):
            if isinstance(od, dict) and od.get('id'):
                created_ids.append(od['id'])
            elif isinstance(od, int):
                created_ids.append(od)
        _logger.info("[VF][POS] created_ids=%s", created_ids)

        if not created_ids:
            _logger.warning("[VF][POS] No hay IDs creados; retorno directo.")
            return created_orders_data

        # C) Post-procesar
        for order in self.browse(created_ids):
            _logger.info("[VF] ▶ Procesando POS %s (id=%s)", (order.name or ''), order.id)

            if order.vf_processed:
                _logger.info("[VF] Idempotencia: ya procesado (order.id=%s).", order.id)
                continue
            order.vf_last_attempt = fields.Datetime.now()

            if not order.partner_id:
                raise UserError(_("Para facturar el ticket es obligatorio seleccionar un cliente en el POS."))

            inv = order._get_invoice()
            if not inv:
                try:
                    if hasattr(order, 'action_pos_order_invoice'):
                        _logger.info("[VF] Creando factura con action_pos_order_invoice()…")
                        order.sudo().action_pos_order_invoice()
                        order.refresh()
                        inv = order._get_invoice()
                    elif hasattr(order, '_create_invoice'):
                        _logger.info("[VF] Creando factura con _create_invoice()…")
                        order.sudo()._create_invoice()
                        order.refresh()
                        inv = order._get_invoice()
                except Exception as e:
                    _logger.error("[VF] Error creando factura desde POS: %s", repr(e))

            if not inv:
                _logger.warning("[VF] Sin documento contable; omito VF/QR (order.id=%s)", order.id)
                order.write({'verifactu_status_pos': False, 'show_qr_always_pos': False, 'qrcode': False, 'qrcode_binary': False})
                continue

            # (1) Fecha + post
            self._set_invoice_date_if_needed(inv)
            self._post_invoice_if_needed(inv)
            inv.refresh()

            # (2) Espera a número definitivo (sin tocar secuencia)
            ok_num, num = self._wait_definitive_number(inv, tries=14, sleep_secs=0.06)
            if not ok_num:
                _logger.warning("[VF] Número no definitivo aún (%s). No envío ni genero hash.", num)
                continue

            # (3) Debe estar posteada
            if not self._invoice_is_posted(inv):
                _logger.warning("[VF] Factura no posteada; omito envío. (id=%s state=%s)", inv.id, getattr(inv, 'state', None))
                continue

            # (4) Config de compañía (fuente de verdad)
            config = self._get_config_for_invoice(inv)
            is_active = self._is_verifactu_active_from_config(config)
            _logger.info("[VF] Estado VF (config): active=%s endpoint=%s mode=%s",
                         is_active, bool((getattr(config, 'endpoint_url', '') or '').strip()),
                         getattr(config, 'verifactu_mode_enabled', False))

            # (5) Recalcular huella con el número fiscal definitivo (con fallback)
            self._force_recompute_verifactu_hash(inv, config=config)
            self._invalidate_existing_fields(inv, 'verifactu_hash', 'verifactu_previous_hash', 'verifactu_status')

            try:
                # (6) Enviar o solo generar según heurística
                if self._should_send_now(inv, config):
                    if hasattr(inv, 'send_xml'):
                        _logger.info("[VF] Enviando a VeriFactu... (invoice id=%s)", inv.id)
                        inv.send_xml()
                        _logger.info("[VF] Envío OK (invoice id=%s)", inv.id)
                else:
                    if hasattr(inv, 'only_generate_xml_never_send'):
                        _logger.info("[VF] Generando XML sin envío… (invoice id=%s)", inv.id)
                        inv.only_generate_xml_never_send()
                        _logger.info("[VF] Generación XML OK (invoice id=%s)", inv.id)

                inv.refresh()

                # (7) QR al pedido (usar is_active para “factura verificable”)
                data_url = False
                try:
                    qr_binary = VerifactuQRContentGenerator(
                        invoice=inv,
                        config=config,
                        factura_verificable=bool(is_active),
                    ).generate_qr_binary()
                    if qr_binary:
                        order.qrcode_binary = qr_binary
                        data_url = "data:image/png;base64,%s" % b64encode(qr_binary).decode()
                        order.qrcode = data_url
                    else:
                        inv_qr = getattr(inv, 'verifactu_qr', False)
                        if inv_qr:
                            order.qrcode_binary = inv_qr
                            data_url = "data:image/png;base64,%s" % b64encode(inv_qr).decode()
                            order.qrcode = data_url
                except Exception as e_qr:
                    _logger.error("[VF] Error generando/copiando QR: %s", repr(e_qr))

                # (8) Cache + bandera
                order.write({
                    'qrcode': data_url or order.qrcode or False,
                    'verifactu_status_pos': getattr(inv, 'verifactu_status', False) or False,
                    'show_qr_always_pos': True,
                    'vf_processed': True,
                })
                _logger.info("[VF] Flujo VeriFactu finalizado para order=%s", order.id)

            except Exception as e:
                _logger.error("[VF] Error en flujo VeriFactu para order=%s: %s", order.id, repr(e))

        # D) Enriquecer retorno (v11)
        for i, od in enumerate(created_orders_data or []):
            if isinstance(od, dict):
                o = self.browse(od.get('id'))
                od.setdefault('qrcode', o.qrcode or False)
                od.setdefault('verifactu_status', o.verifactu_status_pos or o.verifactu_status or False)
                od.setdefault('show_qr_always', bool(o.show_qr_always_pos or o.show_qr_always))

        _logger.info("[VF][POS] create_from_ui FIN")
        return created_orders_data
