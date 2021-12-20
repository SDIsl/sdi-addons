
import base64
import io
from odoo import api, fields, models
import pandas
import logging
_log = logging.getLogger('Importador apertura')
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

_modo_de_pago = {
    'GIRO': 22,
    'Transferencia': 50,
    '-': False,
}


class Importar(models.TransientModel):
    _name = 'importar.apertura'
    _description = 'Importar asiento apertura'

    data_file = fields.Binary(
        string='Excel Sheet',
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
    )
    date = fields.Date(
        string='Date',
    )
    move_id = fields.Many2one(
        comodel_name='account.move',
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
    )

    @api.onchange('data_file')
    def _onchange_data_file(self):
        if not self.data_file:
            return

    def action_import_file(self):
        self.ensure_one()
        cta = self.env['account.account']
        cli = self.env['res.partner']
        aml = self.env['account.move.line']
        asiento = self.env['account.move']
        buf = io.BytesIO()
        buf.write(base64.b64decode(self.data_file))
        df = pandas.read_excel(buf, engine='xlrd')
        if self.move_id:
            asto = self.move_id
        else:
            asto = asiento.create({
                'company_id': self.company_id.id,
                'journal_id': self.journal_id.id,
                'move_type': 'other',
                'ref': 'Apertura',
                'date': self.date,
            })
            self.env.cr.commit()
        asto.line_ids.unlink()

        for linea, row in df.iterrows():
            _log.warning(linea)
            cta_base = str(row['CTA'])[0:2]+'0000'
            row['CTA'] = int(row['CTA'])
            quecta = cta.search([
                ('company_id', '=', asto.company_id.id),
                ('code', '=', str(row['CTA']))])
            partner = False
            if row['NOMBRE'] != "-":
                partner = cli.search([
                    ('is_company', '=', True),
                    ('vat', '=', row['NIF']),
                ], limit=1)
                if not partner:
                    partner = cli.search([
                        ('is_company', '=', True),
                        ('vat', '=', "ES" + str(row['NIF'])),
                    ], limit=1)
                    if not partner:
                        partner = cli.search([
                            ('is_company', '=', True),
                            ('vat', '=', str(row['NIF'])),
                            ('active', '=', False),
                        ], limit=1)
                        if not partner:
                            partner = cli.search([
                                ('is_company', '=', True),
                                ('name', '=', row['NOMBRE']),
                                ('active', '=', False),
                            ], limit=1)
                            if not partner:
                                partner = cli.create({
                                    'name': row['NOMBRE'],
                                    # 'vat': row['NIF'],
                                })
                                self.env.cr.commit()
                quecta = cta.search([
                    ('company_id', '=', asto.company_id.id),
                    ('code', '=', cta_base)])

            debe = row['SALDO'] if int(row['SALDO']) > 0 else 0

            haber = -row['SALDO'] if row['SALDO'] < 0 else 0
            fecha_vencimiento = row['vencimiento'] if row['VTO'] else False
            descripcion = "(%s) APE %s" % (
                row['CTA'],
                row['DESCRIPCION']
            )
            data = {
                'debit': debe,
                'credit': haber,
                'account_id': quecta.id if quecta else self.account_id.id,
                'move_id': asto.id,
                'partner_id': partner.id if partner else False,
                'name': descripcion,
                'payment_mode_id': _modo_de_pago[row['fpago']],
                'date_maturity': fecha_vencimiento,
            }
            aml.with_context(check_move_validity=False).create(data)
            self._cr.commit()
        return
