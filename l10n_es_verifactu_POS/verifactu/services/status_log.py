# -*- coding: utf-8 -*-
from odoo import models, fields, release

# ───────────────────────── Helpers versión ─────────────────────────
def _odoo_major():
    try:
        return int(str(getattr(release, 'major_version', '') or release.version).split('.')[0])
    except Exception:
        return 12

INVOICE_MODEL = 'account.move' if _odoo_major() >= 13 else 'account.invoice'


class VerifactuStatusLog(models.Model):
    _name = "verifactu.status.log"
    _description = "Histórico de cambios de estado VeriFactu"
    _order = "date desc, id desc"

    # ────────────────────────────────
    # Campos base
    # ────────────────────────────────
    invoice_id = fields.Many2one(
        INVOICE_MODEL,            # v12 => account.invoice ; v13+ => account.move
        string="Factura",
        required=True,
        ondelete="cascade",
        index=True,
    )

    def _default_selection_status(self):
        """Compat 12–18: toma la selección del campo verifactu_status si existe; añade estados internos."""
        base_selection = []
        try:
            verifactu_model = self.env[INVOICE_MODEL]
            field = verifactu_model._fields.get("verifactu_status")
            if field and getattr(field, "selection", None):
                base_selection = list(field.selection)
        except Exception:
            base_selection = []

        if not base_selection:
            base_selection = [
                ("draft", "Borrador"),
                ("sent", "Enviado"),
                ("accepted_with_errors", "Aceptado con errores"),
                ("error", "Error"),
            ]

        # Estados internos (no AEAT)
        extra = [
            ("hash_generated", "Sin enviar"),
        ]
        seen = set(k for k, _ in base_selection)
        for k, v in extra:
            if k not in seen:
                base_selection.append((k, v))
        return base_selection

    status = fields.Selection(
        selection=_default_selection_status,
        string="Estado",
        required=True,
    )

    date = fields.Datetime(
        string="Fecha",
        default=lambda self: fields.Datetime.now(),
        required=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="Usuario",
        default=lambda self: self.env.user,
    )

    notes = fields.Text(
        string="Notas (opcional)",
        help="Mensaje complementario sobre el cambio de estado.",
    )

    # ────────────────────────────────
    # Campos de trazabilidad VeriFactu
    # ────────────────────────────────
    hash_actual = fields.Char(
        string="Hash actual",
        size=64,
        help="Huella criptográfica calculada para este estado.",
    )

    hash_previo = fields.Char(
        string="Hash previo",
        size=64,
        help="Huella de la factura anterior en el encadenamiento VeriFactu.",
    )

    # ────────────────────────────────
    # Auditoría / payload AEAT
    # ────────────────────────────────
    xml_soap = fields.Binary(
        string="XML SOAP",
        help="Copia del XML SOAP enviado o generado para esta factura (base64).",
    )

    aeat_code = fields.Integer(
        string="Código AEAT",
        help="Código de respuesta devuelto por la AEAT (p. ej., 4102, 2000, 3000…).",
    )
