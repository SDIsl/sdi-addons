###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from odoo import _
from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition
import ast


class Binary(http.Controller):
    @http.route('/web/binary/download_document_invoice',
                type='http',
                auth='user')
    def download_document_invoice(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        attachment_ids = request.env['ir.attachment'].search([
                ('id', 'in', new_tab)]
            )
        file_dict = {}
        for attachment_id in attachment_ids:
            file_store = attachment_id.store_fname
            if file_store:
                invoice = request.env['account.invoice'].search([
                    ('id', '=', attachment_id.res_id),
                ])
                if not invoice:
                    continue
                attach_name = attachment_id.name.rsplit('.', 1)
                file_name = invoice.date_invoice.strftime('%d_%m_%Y')
                file_name += ' - ' + (invoice.reference or '')
                if invoice.reference != attach_name[0]:
                    file_name += _('- Review - ') + attach_name[0]
                file_name += '.%s' % attach_name[-1]
                file_path = attachment_id._full_path(file_store)
                file_dict['%s:%s' % (file_store, file_name)] = dict(
                    path=file_path,
                    name=file_name)
        zip_filename = '%s.zip' % datetime.now()
        bitIO = BytesIO()
        zip_file = zipfile.ZipFile(bitIO, 'w', zipfile.ZIP_DEFLATED)
        for file_info in file_dict.values():
            zip_file.write(file_info['path'], file_info['name'])
        zip_file.close()
        return request.make_response(
            bitIO.getvalue(),
            headers=[
                ('Content-Type', 'application/x-zip-compressed'),
                ('Content-Disposition', content_disposition(zip_filename))]
            )
