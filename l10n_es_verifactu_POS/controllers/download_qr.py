# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import io
import re
import qrcode


class VerifactuDownloadQRController(http.Controller):
    """
    Descarga del PNG del QR de verificación (Odoo 10→18)
    - Busca el registro por ID en account.invoice y/o account.move.
    - Prefiere el registro que tenga el campo/método del mixin.
    - Si verifactu_qr_url ya tiene valor, lo usa sin regenerar.
    - Si no, intenta get_or_generate_qr_url(); si falla, 409 con diagnóstico.
    """

    # Rutas alternativas para evitar 404 por variaciones
    @http.route(['/verifactu/download_qr/<int:record_id>'], type='http', auth='user', csrf=False)
    def download_qr_by_id(self, record_id, **kwargs):
        invoice = self._resolve_invoice_record(record_id)
        if not invoice:
            return request.not_found()
        return self._make_qr_response(invoice)

    @http.route(['/verifactu/download_qr'], type='http', auth='user', csrf=False)
    def download_qr_by_query(self, **kwargs):
        try:
            record_id = int(kwargs.get('id', '0'))
        except Exception:
            record_id = 0
        if not record_id:
            return request.not_found()
        invoice = self._resolve_invoice_record(record_id)
        if not invoice:
            return request.not_found()
        return self._make_qr_response(invoice)

    @http.route(['/verifactu/download_qr/move/<model("account.move"):invoice>'], type='http', auth='user', csrf=False)
    def download_qr_move(self, invoice, **kwargs):
        return self._make_qr_response(invoice)

    @http.route(['/verifactu/download_qr/invoice/<model("account.invoice"):invoice>'], type='http', auth='user', csrf=False)
    def download_qr_invoice(self, invoice, **kwargs):
        return self._make_qr_response(invoice)

    # ------------------ Helpers ------------------

    def _resolve_invoice_record(self, record_id):
        """
        Devuelve el browse record correcto priorizando:
        1) El que EXISTE y respeta ACLs.
        2) El que TIENE el campo/método del mixin (verifactu_qr_url / get_or_generate_qr_url).
        """
        candidates = []

        # v10–v12
        try:
            inv_legacy = request.env['account.invoice'].browse(record_id)
            if inv_legacy.exists():
                try:
                    inv_legacy.check_access_rights('read')
                    inv_legacy.check_access_rule('read')
                    candidates.append(inv_legacy)
                except Exception:
                    pass
        except Exception:
            pass

        # v13+
        try:
            inv_move = request.env['account.move'].browse(record_id)
            if inv_move.exists():
                try:
                    inv_move.check_access_rights('read')
                    inv_move.check_access_rule('read')
                    candidates.append(inv_move)
                except Exception:
                    pass
        except Exception:
            pass

        if not candidates:
            return False

        # Si alguno tiene el campo/método del mixin, preferirlo
        def _score(rec):
            has_field = hasattr(rec, 'verifactu_qr_url')
            has_method = callable(getattr(rec, 'get_or_generate_qr_url', None))
            return (1 if has_field else 0) + (1 if has_method else 0)

        candidates.sort(key=_score, reverse=True)
        return candidates[0]

    def _make_qr_response(self, invoice):
        """Genera el PNG a partir de la URL; si falta, 409 con diagnóstico claro."""
        # Nombre archivo
        inv_number = (getattr(invoice, 'name', None) or getattr(invoice, 'number', '') or '').strip()
        safe_num = inv_number or 'factura'
        safe_num = re.sub(r'[^\w\-_.]+', '_', safe_num)
        filename = 'verifactu_%s.png' % safe_num

        # 1) Si YA hay URL en el campo, usarla tal cual
        url_existing = ''
        try:
            url_existing = (getattr(invoice, 'verifactu_qr_url', '') or '').strip()
        except Exception:
            url_existing = ''

        if url_existing:
            verification_url = url_existing
        else:
            # 2) Intentar la vía del mixin (misma lógica que en post/open)
            verification_url = ''
            try:
                get_url = getattr(invoice, 'get_or_generate_qr_url', None)
                if callable(get_url):
                    verification_url = (get_url() or '').strip()
                else:
                    # Compat, si el método no está disponible aún
                    regen = getattr(invoice, 'action_regenerate_verifactu_qr_url', None)
                    if callable(regen):
                        regen()
                        verification_url = (getattr(invoice, 'verifactu_qr_url', '') or '').strip()
            except Exception:
                verification_url = ''

        # 3) Sin URL → 409 con diagnóstico
        if not verification_url:
            # Diagnóstico mínimo útil
            model_name = getattr(invoice, '_name', 'unknown')
            has_field = hasattr(invoice, 'verifactu_qr_url')
            field_len = len(url_existing) if url_existing else 0
            has_method = callable(getattr(invoice, 'get_or_generate_qr_url', None))

            reasons = []
            try:
                if bool(getattr(invoice, 'verifactu_noverifactu', False)):
                    reasons.append('modo No VeriFactu activo')
            except Exception:
                pass
            try:
                company = getattr(invoice, 'company_id', False)
                if not company or not request.env['verifactu.endpoint.config'].sudo().search(
                    [('company_id', '=', company.id)], limit=1
                ):
                    reasons.append('configuración de endpoint ausente')
            except Exception:
                pass

            detail = (
                "No se pudo obtener la URL del QR.\n"
                "Diag: model=%s id=%s has_field=%s field_len=%s has_method=%s"
                % (model_name, invoice.id, has_field, field_len, has_method)
            )
            if reasons:
                detail += "\nPosibles causas: " + ", ".join(reasons) + "."

            resp = request.make_response(detail, headers=[('Content-Type', 'text/plain; charset=utf-8')])
            try:
                resp.status_code = 409
            except Exception:
                resp.status = '409 CONFLICT'
            return resp

        # 4) Generar PNG del QR
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=1,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return request.make_response(
            buffer.read(),
            headers=[
                ('Content-Type', 'image/png'),
                ('Content-Disposition', 'attachment; filename="%s"' % filename),
                ('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0'),
                ('Pragma', 'no-cache'),
            ],
        )
