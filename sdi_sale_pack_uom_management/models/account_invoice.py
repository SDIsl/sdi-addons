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
                    if sml.product_id.tracking == 'serial':
                        lot_strings.append('<li>%s %s</li>' % (
                            _('S/N'), sml.lot_id.name,
                        ))
                    else:
                        lot_strings.append('<li>%s %s (%s) F.Cad: %s</li>' % (
                            _('Lot'), sml.lot_id.name, sml.qty_done, (sml.lot_id.expiry_date if sml.lot_id.expiry_date else '----/--/--')
                        ))
            if lot_strings:
                note += ' '.join(lot_strings)
                note += '</ul>'
                line.lot_formatted_note = note
