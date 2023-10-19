###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _compute_last_pos_order(self):
        for pos in self:
            pos.l10n_es_last_pos_order = self.env['pos.order'].search([
                ('config_id', '=', pos.id),
                ('is_l10n_es_simplified_invoice', '=', True)
            ], order='id DESC', limit=1).pos_reference

    l10n_es_last_pos_order = fields.Char(
        string='Last Order',
        readonly=True,
        compute='_compute_last_pos_order'
    )
