###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models, SUPERUSER_ID


class Lead(models.Model):
    _inherit = 'crm.lead'

    def _get_default_lead_stage_id(self):
        default_stage = self.env['crm.lead.stage'].search([], limit=1)
        if default_stage:
            return default_stage.id
        return False

    lead_stage_id = fields.Many2one(
        comodel_name='crm.lead.stage',
        string='Etapa de la iniciativa',
        tracking=True,
        default=lambda self: self._get_default_lead_stage_id(),
        group_expand='_read_group_lead_stage_ids',
    )

    @api.model
    def _read_group_lead_stage_ids(self, lead_stages, domain, order):
        statuse_ids = lead_stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return lead_stages.browse(statuse_ids)
