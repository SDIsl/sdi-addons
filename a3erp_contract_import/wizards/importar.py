import base64
import io
from odoo import api, fields, models, _
import pandas
import logging
_log = logging.getLogger('SDi migration res_partner')
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

from base64 import b64decode
import json
from os import path


class Importar(models.TransientModel):
    _name = 'importar.contratos'
    _description = 'Importador de contratos'

    data_file = fields.Binary(
        string='Hoja de Excel',
        required=True,
    )
    company_id = fields.Many2one('res.company')
    cliente = fields.Char("Cliente", default='codcli')
    nombre = fields.Char("Nombre contrato", default='contract_id')
    producto = fields.Char("Producto", default="codart")
    uds = fields.Char("Unidades", default="quantity")
    precio_u = fields.Char("precio", default="price_unit")
    descuento = fields.Char("Descuento", default="multiple_discount")
    intervalo_num = fields.Char("Intervalo ctd", default="recurring_interval")
    intervalo_tipo = fields.Char("Intervalo regla", default="recurring_rule_type")
    fecha_comienzo = fields.Char("Fecha comienzo", default="date_start")
    fecha_fin = fields.Char("Fecha fin", default="date_end")
    fecha_siguiente = fields.Char("Fecha siguiente", default="recurring_next_date")

    @api.onchange('data_file')
    def _onchange_data_file(self):
        if not self.data_file:
            return

    @api.multi
    def button_importar(self):
        self.ensure_one()
        cabe = self.env['contract.contract']
        line = self.env['contract.line']
        prod = self.env['product.product']
        cli = self.env['res.partner']
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
        ], limit=1).id
        buf = io.BytesIO()
        buf.write(base64.b64decode(self.data_file))
        df = pandas.read_excel(buf, engine='xlrd')
        curcli = cli
        curcon = cabe.name
        for linea, row in df.iterrows():
            _log.info(linea)
            cliente = cli.search([('migration_customer_id', '=', str(int(row[self.cliente])))])
            if not cliente:
                _log.warning("El cliente (%s) no se encuentra." % str(int(row[self.cliente])))
                continue
            producto = prod.search([('default_code', '=', row[self.producto])])
            if not producto:
                _log.warning("El producto (%s) no se encuentra." % row[self.producto])
                continue
            if curcli != cliente or curcon.name != row[self.nombre]:
                # Crear cabecera de contrato
                contract = cabe.create(
                    {
                        'partner_id': cliente.id,
                        'company_id': self.company_id.id,
                        'name': row[self.nombre],
                        'journal_id': journal,
                        'recurring_next_date': row[self.fecha_siguiente],
                        'payment_term_id': cliente.property_payment_term_id.id,
                        'payment_mode_id': cliente.customer_payment_mode_id.id,
                        'unit_id': producto.unit_id.id,

                    })
            contract_line = line.create(
                {
                    'contract_id': contract.id,
                    'product_id': producto.id,
                    'name': producto.name,
                    'date_start': row[self.fecha_comienzo],
                    'date_end': row[self.fecha_fin],
                    'recurring_next_date': row[self.fecha_siguiente],
                    'quantity': row[self.uds],
                    'uom_id': producto.uom_id.id,
                    'specific_price': row[self.precio_u],
                    'discount': row[self.descuento],
                    'recurring_interval': row[self.intervalo_num],
                    'recurring_interval_type': row[self.intervalo_tipo],

                }
            )
            curcli = cliente
            curcon = contract

        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': 'contract.action_customer_contract',
            'view_mode': 'tree,form',
            'res_model': 'contract.contract',
            'context': {'create_uid': self.env.user.id, 'company_id': self.company_id.id},
        }

