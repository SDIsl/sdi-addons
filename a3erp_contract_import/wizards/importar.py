
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


_recurring_rule_type = {
    'anual': 'yearly',
    'meses': 'monthly',
    'yearly': 'yearly',
}


class Correlacion(models.Model):
    _name = "importar.contratos.correlacion"
    name = fields.Char("Cod a3ERP")
    product_id = fields.Many2one(
        "product.product"
    )


class Errores(models.TransientModel):
    _name = "importar.contratos.errores"
    linea = fields.Integer()
    name = fields.Char("Error")


class ContractLine(models.Model):
    _inherit = 'contract.line'
    a3erp_id = fields.Char('id a3ERP')


class Importar(models.TransientModel):
    _name = 'importar.contratos'
    _description = 'Importador de contratos'

    data_file = fields.Binary(
        string='Hoja de Excel',
        required=True,
    )
    company_id = fields.Many2one('res.company')
    cliente = fields.Char("Cliente", default='idcliente')
    nif_cliente = fields.Char("NIF", default="nifcli")
    nombre = fields.Char("Nombre contrato", default='contrato')
    producto = fields.Char("Producto", default="idprod")
    uds = fields.Char("Unidades", default="cantidad")
    precio_u = fields.Char("precio", default="precio_u")
    descuento = fields.Char("Descuento", default="texto_descuento")
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
        error.search([]).unlink()
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
            pk = '%s%s' % (row['idcuota'], row['DESCART'])
            if line.search([('a3erp_id', '=', pk)]):
                continue
            _log.warning(linea)
            cliente = '' # cli.search([('migration_customer_id', '=', str(row[self.cliente]))])
            if not cliente:
                cliente = cli.search([
                    ('is_company', '=', True),
                    ('active', '=', True),
                    ('vat', '=', row[self.nif_cliente]),
                ], limit=1)
                if not cliente:
                    cliente = cli.search([
                        ('is_company', '=', True),
                        ('active', '=', True),
                        ('vat', '=', 'ES%s' % row[self.nif_cliente]),
                    ], limit=1)
            if not cliente:
                _log.warning("El cliente (%s) no se encuentra. Contrato: %s " % (str(int(row[self.cliente])),
                                                                                 row[self.nombre]))
                error.create({
                    'linea': linea+2,
                    'name': "El cliente (%s) %s no se encuentra. Contrato: %s " % (
                        str(int(row[self.cliente])),
                        row['nomcli'],
                        row[self.nombre])
                })
                continue
            producto = prod.search([('default_code', '=', row[self.producto])])
            if not producto:
                producto = self.env['importar.contratos.correlacion'].search(
                    [('name', '=', row[self.producto])])
                if producto:
                    producto = producto.product_id
                if not producto:
                    producto = prod.search([('active', '=', False),
                                            ('default_code', '=', row[self.producto])])
                    if producto:
                        _log.warning("El producto (%s) está ARCHIVADO. Contrato: %s del cliente %s" % (
                            row[self.producto], row[self.nombre], cliente.name))
                        error.create({
                            'linea': linea + 2,
                            'name': "El producto (%s) está ARCHIVADO. Contrato: %s del cliente %s" %
                                    (row[self.producto], row[self.nombre], cliente.name)
                        })
                        continue
                    else:
                        _log.warning("El producto (%s) %s no se encuentra. Contrato: %s del cliente %s" % (
                            row[self.producto],
                            row['DESCART'],
                            row[self.nombre], cliente.name))
                        error.create({
                            'linea': linea + 2,
                            'name': "El producto (%s) %s no se encuentra. Contrato: %s del cliente %s" %
                                    (row[self.producto], row['DESCART'], row[self.nombre], cliente.name)
                        })
                        continue
            if producto.unit_id.company_id.id != self.company_id.id:
                _log.warning("El producto (%s) tiene udn que pertenece a %s " %
                             (row[self.producto], producto.unit_id.company_id.name))
                error.create({
                    'linea': linea + 2,
                    'name': "El producto (%s) tiene udn que pertenece a %s " %
                            (row[self.producto], producto.unit_id.company_id.name)
                })
                continue
            if row[self.fecha_siguiente] < row[self.fecha_comienzo]:
                _log.warning("Fecha de proxima factura anterior a fecha de inicio de contrato: %s de %s " %
                             (row[self.nombre], cliente.name))
                error.create({
                    'linea': linea + 2,
                    'name': "Fecha de proxima factura anterior a fecha de inicio de contrato: %s de %s " %
                            (row[self.nombre], cliente.name)
                })
                continue
            descuento = "%s+%s+%s+%s" % (
                abs(row['desc1']),
                abs(row['desc2']),
                abs(row['desc3']),
                abs(row['desc4']),
            )
            if descuento == '0+0+0+0':
                descuento = ''
            nombre_descuento = str(row[self.descuento]) if row[self.descuento] else False
            if nombre_descuento == "nan":
                nombre_descuento = ""
            # contract = False
            # contract_template_id = False
            # Unidad de medida
            cadencia = _recurring_rule_type[row[self.intervalo_tipo]]
            intervalo = row[self.intervalo_num]
            if cadencia == 'monthly':
                udm = 20 if intervalo == 1 else 24 if intervalo == 3 else 22
            else:
                udm = 21
            # Descripción de la linea:
            descrip = row['DESCART']
            if type(row['Texto']) is str:
                descrip += '\n' + row['Texto']
            #
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
                        'contract_template_id': producto.property_contract_template_id.id,
                    })

            contract_line = line.create(
                {
                    'contract_id': contract.id,
                    'a3erp_id': pk,
                    'product_id': producto.id,
                    'name': descrip,
                    'date_start': row[self.fecha_comienzo],
                    # 'date_end': row[self.fecha_fin],
                    'recurring_next_date': row[self.fecha_siguiente],
                    'quantity': row[self.uds],
                    'uom_id': udm,
                    'specific_price': row[self.precio_u],
                    'multiple_discount': descuento if descuento else '',
                    'discount_name': nombre_descuento,
                    'recurring_interval': intervalo,
                    'recurring_rule_type': cadencia,

                }
            )
            self.env.cr.commit()
            curcli = cliente
            curcon = contract
            contract_template_id = producto.property_contract_template_id.id

        return {
            'type': 'ir.actions.act_window',
            'target': 'self',
            'name': 'Errores en la migracion',
            'view_mode': 'tree,form',
            'res_model': 'importar.contratos.errores',
        }

    def action_borrar_facturas(self):
        borrar = self.env['contract.contract'].search([('company_id', '=', 1)]).unlink()
        facturas = self.env['account.invoice'].search([
            ('company_id', '=', 1),
            ('state', '=', 'draft'),
        ])
        for factura in facturas:
            for linea in factura.invoice_line_ids:
                if linea.advance_line_id:
                    linea.advance_line_id.unlink()
                for lineaventa in linea.sale_line_ids:
                    lineaventa.order_id.state = "done"
            factura.unlink()
        return 0
