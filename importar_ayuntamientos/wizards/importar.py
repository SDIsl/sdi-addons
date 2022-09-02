
import base64
import io
from odoo import api, fields, models, _
import pandas
import logging
from base64 import b64decode
import json
from os import path

_log = logging.getLogger('SDi migration contracts')
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None


class Importar(models.TransientModel):
    _name = 'importar.ayuntamientos'
    _description = 'Importador de ayuntamientos'

    data_file = fields.Binary(
        string='Hoja de Excel',
        required=True,
    )

    @api.onchange('data_file')
    def _onchange_data_file(self):
        if not self.data_file:
            return

    @api.multi
    def button_importar(self):
        self.ensure_one()
        cli = self.env['res.partner']
        buf = io.BytesIO()
        buf.write(base64.b64decode(self.data_file))
        resultado = []
        df = pandas.read_excel(buf, engine='xlrd')
        curcli = cli
        for linea, row in df.iterrows():
            update = True
            ayto = False
            ayto = cli.search([('name', '=', row['NombreAyuntamiento'])])
            if not ayto:
                ayto = cli.search([
                    ('industry_id', '=', 120),
                    ('zip', '=', row['CP']),
                    ('city', '=', row['POBLACION']),
                    ('is_company', '=', True),
                 ])

            provincia = self.env['res.city.zip'].search([('name', '=', str(row['CP']).zfill(5))])[0].city_id.state_id

            if not ayto:
                ayto = cli.create({
                    'name': row['NombreAyuntamiento'],
                    'industry_id': 120,
                    'company_type': 'company',
                    'customer': True,
                })
                _log.warning(ayto.name + ' CREADO')
            else:
                if not ayto[0].num_inhabitants:
                    ayto[0].write({
                        'num_inhabitants': row['HABITANTES'],
                    })
                else:
                    update = False
                if ayto.sale_order_count or ayto.customer_type:
                    update = False
                    _log.warning(ayto.name + ' OMITIDO')
                else:
                    _log.warning(ayto.name + ' ACTUALIZADO')

            if update:
                ayto[0].write({
                    'name': row['NombreAyuntamiento'],
                    'city': row['POBLACION'],
                    'state_id': provincia.id,
                    'country_id': provincia.country_id.id,
                    'street': row['DIRECCION'],
                    'zip': row['CP'],
                    'email': row['EMAIL'],
                    'phone': row['TELEFONO'],
                })
                contacto = cli.search([
                    ('parent_id', '=', ayto.id),
                    ('name', '=', row['ALCALDE']),
                ])
                if not contacto:
                    cli.create({
                        'company_type': 'person',
                        'name': row['ALCALDE'],
                        'comment': row['PARTIDO'],
                        'function': 'ALCALDE/ALCALDESA',
                        'parent_id': ayto.id
                    })
            self.env.cr.commit()
        return {}
