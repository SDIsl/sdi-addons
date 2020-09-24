
import base64
import io
from odoo import api, fields, models, _
import pandas
import logging
_log = logging.getLogger('SDi migration contracts')
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

_recurring_rule_type = {
    'anual': 'yearly',
    'meses': 'monthly',
}


class Errores(models.Model):
    _name = "importar.contratos.errores"
    linea = fields.Integer()
    name = fields.Char("Error")


class Importar(models.TransientModel):
    _name = 'importar.contratos'
    _description = 'Importador de contratos'

    data_file = fields.Binary(
        string='Hoja de Excel',
        required=True,
    )
    company_id = fields.Many2one('res.company')
    cliente = fields.Char("Cliente", default='idcliente')
    nombre = fields.Char("Nombre contrato", default='contrato')
    producto = fields.Char("Producto", default="idprod")
    uds = fields.Char("Unidades", default="cantidad")
    precio_u = fields.Char("precio", default="precio_u")
    descuento = fields.Char("Descuento", default="descuento")
    intervalo_num = fields.Char("Intervalo ctd", default="frecuencia")
    intervalo_tipo = fields.Char("Intervalo regla", default="frecuencia_tiempo")
    fecha_comienzo = fields.Char("Fecha comienzo", default="fecha inicio")
    fecha_fin = fields.Char("Fecha fin", default="fecha fin")
    fecha_siguiente = fields.Char("Fecha siguiente", default="fecha proxima factura")

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
        error = self.env['importar.contratos.errores']
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
            cliente = cli.search([('migration_customer_id', '=', str(row[self.cliente]))])
            if not cliente:
                _log.warning("El cliente (%s) no se encuentra. Contrato: %s " % (str(int(row[self.cliente])),
                                                                                 row[self.nombre]))
                error.create({
                    'linea': linea+2,
                    'name': "El cliente (%s) no se encuentra. Contrato: %s " % (str(int(row[self.cliente])),
                                                                                row[self.nombre])
                })
                continue
            producto = prod.search([('default_code', '=', row[self.producto])])
            if not producto:
                producto = prod.search([('migration_id', '=', row[self.producto])])
                if not producto:
                    producto = prod.search([('migration_original_id', '=', row[self.producto])])
            if not producto:
                _log.warning("El producto (%s) no se encuentra. Contrato: %s del cliente %s" % (row[self.producto],row[self.nombre],cliente.name))
                error.create({
                    'linea': linea + 2,
                    'name': "El producto (%s) no se encuentra. Contrato: %s del cliente %s" %
                            (row[self.producto], row[self.nombre], cliente.name)
                })
                continue
            if producto.area_id.company_id.id != self.company_id.id:
                _log.warning("El producto (%s) tiene udn que pertenece a %s " %
                             (row[self.producto], producto.area_id.company_id.name))
                error.create({
                    'linea': linea + 2,
                    'name': "El producto (%s) tiene udn que pertenece a %s " %
                            (row[self.producto], producto.area_id.company_id.name)
                })
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
                    'recurring_rule_type': _recurring_rule_type[row[self.intervalo_tipo]],

                }
            )
            curcli = cliente
            curcon = contract

        return {
            'type': 'ir.actions.act_window',
            'target': 'self',
            'name': 'Errores en la migracion',
            'view_mode': 'tree,form',
            'res_model': 'importar.contratos.errores',
        }

