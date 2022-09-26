###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import logging
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from datetime import datetime
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import content_disposition
import ast

_logger = logging.getLogger(__name__)


class Binary(http.Controller):
    @http.route('/web/binary/download_document_item',
                type='http',
                auth='user')
    def download_document_item(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        attachment_ids = request.env['ir.attachment'].search([
                ('id', 'in', new_tab)]
            )
        file_dict = {}
        for attachment_id in attachment_ids:
            file_store = attachment_id.store_fname
            if file_store:
                item = request.env['workspace.item'].search([
                    ('id', '=', attachment_id.res_id),
                ])
                if not item:
                    continue
                # employee = item.employee_id

                file_name = item.name

                if item.workspace_location:
                    file_name += ' - ' + item.workspace_location
                elif item.employee_location:
                    file_name += ' - ' + item.employee_location
                # if employee:
                #    file_name += ' - ' + employee.name

                file_name += ' - ' + attachment_id.name

                file_path = attachment_id._full_path(file_store)
                file_dict['%s:%s' % (file_store, file_name)] = dict(
                    path=file_path,
                    name=file_name)
        zip_filename = datetime.now()
        zip_filename = '%s.zip' % zip_filename
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
