
import base64
import io
from odoo import api, fields, models
import pandas
import logging
import numpy as np

_log = logging.getLogger('SDi migration bancos')
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None


class Importar(models.TransientModel):
    _name = 'importar.bancos'
    _description = 'Importador de bancos'

    data_file = fields.Binary(
        string='Hoja de Excel',
        required=True,
    )
    company_id = fields.Many2one('res.company')

    @api.onchange('data_file')
    def _onchange_data_file(self):
        if not self.data_file:
            return

    def button_importar(self):
        self.ensure_one()
        rpb = self.env['res.partner.bank']
        abm = self.env['account.banking.mandate']
        cli = self.env['res.partner']
        buf = io.BytesIO()
        buf.write(base64.b64decode(self.data_file))
        df = pandas.read_excel(buf, engine='xlrd')
        df = df.replace({np.nan: None})
        for linea, row in df.iterrows():
            _log.warning("%s - %s (%s)" %
                         (linea + 2,
                          row['NOMCLI'],
                          row['CTA'])
                         )
            # valido = (row['FIRMADO'] == "SI")
            # Primer paso: Localizar banco
            if row['CTA'] == "":
                _log.warning('Cta en blanco')
                continue
            banco = rpb.search([
                ('acc_number', '=', row['CTA'])], limit=1)
            cliente = cli.search([
                ('vat', '=', row['NIFCLI']),
                ('is_company', '=', True),
                ('parent_id', '=', False),
            ])
            if not cliente:
                _log.warning("No encuentro el NIF %s" % row['NIFCLI'])
                continue
            if not banco:
                banco = rpb.create({
                    'acc_number': row['CTA'],
                    'partner_id': cliente.id,
                    'acc_type': 'iban',
                    'acc_holder_name': row['NOMCLI'],
                })
                self.env.cr.commit()
            else:
                if banco.company_id and banco.company_id != self.company_id:
                    banco = rpb.create({
                        'acc_number': row['CTA'],
                        'partner_id': cliente.id,
                        'acc_type': 'iban',
                        'acc_holder_name': row['NOMCLI'],
                        'company_id': self.company_id.id,
                    })
                    self.env.cr.commit()
            mandato = abm.search([
                ('partner_id', '=', cliente.id),
                ('company_id', '=', self.company_id.id),
            ])
            if not mandato:
                mandato = abm.search([
                    ('unique_mandate_reference', '=', row['MANDATOREF']),
                    ('company_id', '=', self.company_id.id),
                ])
                if mandato:
                    _log.warning(mandato.unique_mandate_reference)
                    continue
                fecha = row['MANDATOFECHACONFIRMADO']
                data = {
                    'company_id': self.company_id.id,
                    'format': 'sepa',
                    'partner_bank_id': banco.id,
                    'partner_id': cliente.id,
                    'scheme': 'CORE',
                    'signature_date': fecha if fecha != 'nan' else False,
                    'state': 'valid' if fecha else 'draft',
                    'type': 'recurrent',
                    'unique_mandate_reference': row['MANDATOREF'],
                    'recurrent_sequence_type': 'recurring',
                }
                mandato = abm.create(data)
                self.env.cr.commit()
                '''if valido:
                    mandato.signature_date = row['MANDATOFECHACONFIRMADO']
                    mandato.state ='valid' '''

                self.env.cr.commit()
        return
