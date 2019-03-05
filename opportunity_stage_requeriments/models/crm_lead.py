# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, _
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    @api.constrains('stage_id')
    def _onchange_stage_id_check(self):
        """
        Check that the opportunity can change from one stage to another
        depending on if it has data of the requirements that each one requires.

        :raises: UserError
        """
        if self.stage_id.revenue or self.stage_id.deadline or self.stage_id.tags:
            if not self.date_deadline or self.planned_revenue <= 0 or not self.tag_ids:
                err_msg = _("""
                            You can not change status if the opportunity lacks:
                            - deadline
                            - quantity greater than 0
                            - label
                            """)
                raise UserError(_(err_msg))

        if self.stage_id.attachment:
            attach = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'),
                                                       ('res_id', '=', self.id)])
            if not attach:
                err_attachment = _("""
                                You can not change status if the opportunity lacks:
                                 - attached document.
                                """)
                raise UserError(_(err_attachment))

        if self.stage_id.notification:
            responsible = [self.stage_id.responsible.partner_id.id]
            subtyte_id = self.env.ref('mail.mt_comment').id
            for lead in self:
                message = _('<p>Proposal to checked from: <strong>%s</strong></p>'
                            '<p>Lead: <strong>%s</strong></p>' % (lead.user_id.name, lead.name))
                lead.message_post(subject="Proposal to checked from: %s" % lead.user_id.name,
                                  body=message,
                                  subtype_id= subtyte_id,
                                  partner_ids= responsible,
                                  mail_post_autofollow=False)
