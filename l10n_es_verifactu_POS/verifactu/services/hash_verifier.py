# -*- coding: utf-8 -*-
from odoo.tools.translate import _
import re

_HEX64 = re.compile(r'^[0-9A-Fa-f]{64}$')

def _hex64(x):
    """Normaliza hash a HEX64 mayúsculas sin espacios."""
    if not x:
        return ''
    s = (x if isinstance(x, str) else str(x)).strip().replace(' ', '').upper()
    return s if _HEX64.match(s) else ''


class VerifactuHashVerifier(object):
    """
    Verifica la integridad del encadenamiento VeriFactu:
      • Compara el hash GUARDADO con el último hash ENVIADO (log).
      • Comprueba que prev_hash de cada factura == último hash ENVIADO de la anterior.
      • Evita problemas de caché ORM (recarga siempre desde base de datos).
      • Compatible con Odoo 10–18.
    """

    def __init__(self, invoice, config, depth=5):
        self.invoice = invoice
        self.config = config
        self.depth = depth

    # ─────────────────────────────
    # Utilidades
    # ─────────────────────────────
    def _inv_number(self, inv):
        return (
            getattr(inv, "number", None)
            or getattr(inv, "name", None)
            or getattr(inv, "move_name", None)
            or (str(inv.id) if inv else "–")
        )

    def _short(self, h):
        return (h or "")[:16]

    def _field_exists(self, model, field_name):
        try:
            return field_name in getattr(model, "_fields", {}) or field_name in getattr(model, "_columns", {})
        except Exception:
            return False

    def _invoice_model(self, env):
        """Detecta el modelo correcto según qué modelo tiene el campo verifactu_hash."""
        if "account.invoice" in env and "verifactu_hash" in env["account.invoice"]._fields:
            return "account.invoice"
        elif "account.move" in env and "verifactu_hash" in env["account.move"]._fields:
            return "account.move"
        # fallback
        return "account.invoice" if "account.invoice" in env else "account.move"


    def _last_sent_log(self, inv):
        """Devuelve el último log enviado de esa factura."""
        Log = inv.env["verifactu.status.log"]
        return Log.search(
            [
                ("invoice_id", "=", inv.id),
                ("status", "in", ["sent", "accepted_with_errors", "canceled"]),
            ],
            order="date desc, id desc",
            limit=1,
        )

    # ─────────────────────────────
    # Verificación principal
    # ─────────────────────────────
    def verify(self):
        inv = self.invoice
        inv.ensure_one()

        # 🔄 Refrescar desde la base de datos (evita leer caché)
        env = inv.env
        env.cr.commit()
        inv = env[inv._name].browse(inv.id)

        model_name = self._invoice_model(env)
        Model = env[model_name]
        table = Model._table

        # Campo de fecha compatible
        if self._field_exists(Model, "invoice_date"):
            order_field = "invoice_date"
        elif self._field_exists(Model, "date_invoice"):
            order_field = "date_invoice"
        elif self._field_exists(Model, "date"):
            order_field = "date"
        else:
            order_field = "id"

        # Validar que los campos existen antes del SQL
        if not self._field_exists(Model, "verifactu_hash"):
            inv.message_post(body="🟡 " + _("El modelo %s no tiene campo verifactu_hash.") % model_name)
            return True

        # Facturas del mismo diario (máximo depth)
        journal_id = getattr(inv, "journal_id", False)
        domain_sql = "WHERE 1=1"
        if journal_id:
            domain_sql += " AND journal_id = %s" % journal_id.id

        sql = f"""
            SELECT id, verifactu_hash, verifactu_previous_hash
            FROM {table}
            {domain_sql}
            ORDER BY {order_field} DESC, id DESC
            LIMIT {self.depth}
        """

        env.cr.execute(sql)
        rows = env.cr.fetchall()
        if not rows:
            inv.message_post(body="🟡 " + _("No hay facturas suficientes para verificar el encadenamiento."))
            return True

        # ─────────────────────────────
        # Procesar resultados
        # ─────────────────────────────
        invoices = list(reversed(rows))
        log_lines, ok_chain = [], True
        prev_doc_id = None
        last_sent_hash_prev_doc = ""

        for idx, (doc_id, hash_now, hash_prev) in enumerate(invoices, start=1):
            doc = Model.browse(doc_id).sudo()
            doc.invalidate_cache(['verifactu_hash', 'verifactu_previous_hash'])

            num = self._inv_number(doc)
            current_hash = _hex64(hash_now)
            prev_hash = _hex64(hash_prev)

            last_log = self._last_sent_log(doc)
            last_sent_hash_this = _hex64(last_log.hash_actual) if last_log else ""

            # Comparación con el último hash enviado
            if last_sent_hash_this:
                if current_hash == last_sent_hash_this:
                    log_lines.append(
                        f"<b>{idx}. {num}:</b> ✅ { _('Coincide con el último hash enviado') } "
                        f"(<code>{self._short(current_hash)}</code>)"
                    )
                else:
                    ok_chain = False
                    log_lines.append(
                        f"<b>{idx}. {num}:</b> 🛑 <b>CAMBIO</b> — actual=<code>{self._short(current_hash or '-') }</code> "
                        f"último_enviado=<code>{self._short(last_sent_hash_this or '-') }</code>"
                    )
                    log_lines.append("<i>⚠️ La factura fue modificada tras su envío a VeriFactu.</i>")
            else:
                log_lines.append(
                    f"<b>{idx}. {num}:</b> 🛈 Sin envíos previos — hash actual=<code>{self._short(current_hash or '-') }</code>"
                )

            # Encadenamiento
            if idx == 1:
                log_lines.append(f"ℹ️ {num}: Primera factura del diario, no aplica encadenamiento previo.")
            elif last_sent_hash_prev_doc:
                if prev_hash != last_sent_hash_prev_doc:
                    alt = env["verifactu.status.log"].search([("hash_actual", "=", prev_hash)], limit=1)
                    if alt:
                        log_lines.append(
                            f"ℹ️ Encadenamiento alternativo válido: prev_hash=<code>{self._short(prev_hash)}</code> "
                            f"coincide con hash enviado en otra factura."
                        )
                    else:
                        ok_chain = False
                        prev_name = self._inv_number(Model.browse(prev_doc_id)) if prev_doc_id else "–"
                        log_lines.append(
                            f"⚠️ Ruptura de cadena entre <b>{prev_name}</b> → <b>{num}</b> "
                            f"(prev_hash=<code>{self._short(prev_hash)}</code> "
                            f"vs esperado=<code>{self._short(last_sent_hash_prev_doc)}</code>)"
                        )

            last_sent_hash_prev_doc = last_sent_hash_this or ""
            prev_doc_id = doc_id

        # Resultado final
        summary = (
            "🟢 <b>Cadena de integridad verificada correctamente.</b>"
            if ok_chain
            else "🔴 <b>Se detectaron discrepancias o rupturas en la cadena de hash.</b>"
        )

        html = f"{summary}<br/><br/>{'<br/>'.join(log_lines)}"
        inv.message_post(body=html, subtype_xmlid="mail.mt_note")

        return True
