from odoo.exceptions import UserError
from odoo import _
from ..services.logger import VerifactuLogger


class VerifactuChainVerifier:
    def __init__(self, invoice):
        self.invoice = invoice
        
    def verify(self):
        invoice = self.invoice
        invoice.ensure_one()
        logger = VerifactuLogger(invoice)

        try:
            inv_no = getattr(invoice, 'number', None) or getattr(invoice, 'name', '')
            if not invoice.verifactu_previous_hash:
                logger.log(f"✅ Encadenamiento verificado para la primera factura {inv_no} (sin hash anterior)")
                return True

            # v12: open/paid; v13+: posted
            state_sel = dict(invoice._fields['state'].selection or [])
            allowed_states = ('posted',) if 'posted' in state_sel else ('open', 'paid')

            domain = [
                ('company_id', '=', invoice.company_id.id),
                ('verifactu_hash', '!=', False),
                ('date_invoice', '<=', invoice.date_invoice),
                ('id', '!=', invoice.id),
                ('type', 'in', ('out_invoice', 'out_refund')),
                ('state', 'in', allowed_states),
            ]

            logger.log(f"🔍 Buscando factura anterior para encadenar. Dominio: {domain}")

            previous_invoice = invoice.env['account.invoice'].search(
                domain,
                order='date_invoice desc, id desc',
                limit=1,
            )

            if previous_invoice:
                prev_no = getattr(previous_invoice, 'number', None) or getattr(previous_invoice, 'name', '')
                logger.log(f"📄 Factura encontrada: {prev_no} con hash {previous_invoice.verifactu_hash}")
            else:
                logger.log("⚠️ No se encontró ninguna factura anterior válida para encadenar.")

            if previous_invoice and previous_invoice.verifactu_hash == invoice.verifactu_previous_hash:
                prev_no = getattr(previous_invoice, 'number', None) or getattr(previous_invoice, 'name', '')
                logger.log(
                    f"✅ Encadenamiento verificado para la factura {inv_no}.\n"
                    f"Hash anterior esperado: {invoice.verifactu_previous_hash}\n"
                    f"Hash real de la factura previa ({prev_no}): {previous_invoice.verifactu_hash}"
                )
                return True
            else:
                logger.log(
                    f"🛑 Encadenamiento NO verificado para la factura {inv_no}.\n"
                    f"Hash anterior esperado: {invoice.verifactu_previous_hash or '—'}\n"
                    f"Hash real de la factura previa: "
                    f"{previous_invoice.verifactu_hash if previous_invoice else 'Factura previa no encontrada'}"
                )
                return False

        except Exception as e:
            logger.log(f"🛑 Error al verificar el encadenamiento: {str(e)}")
            # Si prefieres no interrumpir al usuario, quita la excepción y devuelve False
            raise UserError(_("Error al verificar el encadenamiento: %s") % e)

