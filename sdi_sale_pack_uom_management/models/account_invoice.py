from datetime import datetime
from odoo import _, api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _compute_line_lots(self):
        for line in self:
            note = '<ul>'
            lot_strings = []
            for sml in line.mapped('move_line_ids.move_line_ids'):
                if sml.lot_id:
                    caduca = ""
                    if sml.lot_id.expiry_date:
                        f = sml.lot_id.expiry_date.split('-')
                        caduca = "F.Cad: %s/%s/%s" % (f[2], f[1], f[0])
                    if sml.product_id.tracking == 'serial':
                        lot_strings.append('<li>%s %s</li>' % (
                            _('S/N'), sml.lot_id.name,
                        ))
                    else:
                        lot_strings.append('<li><i>%s %s (%s) %s</i></li>' % (
                            _('Lot'), sml.lot_id.name, sml.qty_done, caduca
                        ))
            if lot_strings:
                note += ' '.join(lot_strings)
                note += '</ul>'
                line.lot_formatted_note = note
