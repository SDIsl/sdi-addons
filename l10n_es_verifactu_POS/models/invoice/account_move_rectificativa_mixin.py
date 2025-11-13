# -*- coding: utf-8 -*-
from odoo import models

class AccountMoveRectificativaMixin(models.AbstractModel):
    _name = "account.move.rectificativa.mixin"
    _description = "Mixin universal para detectar facturas rectificativas"

    @staticmethod
    def is_rectificativa(invoice):
        """
        Devuelve True si la factura es rectificativa (nota de crédito o abono).
        Compatible con Odoo 10–18 y Python 2/3.
        """
        if not invoice:
            return False

        # ----------------------------
        # Compatibilidad Odoo 10–12
        # ----------------------------
        if hasattr(invoice, 'type') and invoice.type in ('out_refund', 'in_refund'):
            return True
        if hasattr(invoice, 'refund_invoice_id') and invoice.refund_invoice_id:
            return True

        # ----------------------------
        # Compatibilidad Odoo 13+
        # ----------------------------
        if hasattr(invoice, 'move_type') and invoice.move_type in ('out_refund', 'in_refund'):
            return True
        if hasattr(invoice, 'reversed_entry_id') and invoice.reversed_entry_id:
            return True

        return False

    @staticmethod
    def is_refund(invoice):
        """Alias semántico (equivalente a is_rectificativa)."""
        return AccountMoveRectificativaMixin.is_rectificativa(invoice)
