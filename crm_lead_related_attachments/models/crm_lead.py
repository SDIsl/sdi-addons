###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    attachment_count = fields.Integer(
        string='Number of attachments related',
        compute='_compute_attachment_count',
    )

    def _compute_attachment_count(self):
        Attachment = self.env['ir.attachment']
        for lead in self:
            lead.attachment_count = Attachment.search_count([
                '|',
                '&',
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id),
                '&',
                ('res_model', '=', 'sale.order'),
                ('res_id', 'in', lead.order_ids.ids)
            ])

    def attachment_related_view(self):
        action = self.env['ir.actions.act_window'].\
            _for_xml_id('base.action_attachment')

        action['domain'] = str([
            '|',
            '&',
            ('res_model', '=', 'crm.lead'),
            ('res_id', 'in', self.ids),
            '&',
            ('res_model', '=', 'sale.order'),
            ('res_id', 'in', self.order_ids.ids)
        ])

        action['context'] = "{'default_res_model': '%s','default_res_id': %d}"\
            % (self._name, self.id)
        return action
