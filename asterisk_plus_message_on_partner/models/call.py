
import logging
from odoo import models, api, _

logger = logging.getLogger(__name__)


class Call(models.Model):
    _inherit = 'asterisk_plus.call'

    @api.constrains('is_active')
    def register_reference_call(self):
        self.ensure_one()
        for rec in self:
            if rec.is_active:
                continue
            if rec.ref:
                try:
                    direction = 'outgoing' if rec.direction == 'out' else \
                        'incoming'
                    if rec.called_user:
                        message = _('{} {} call to {}. Duration: {}').format(
                            rec.status.capitalize(),
                            direction,
                            rec.called_user.name,
                            rec.duration_human)
                    elif rec.calling_user:
                        message = _(
                            '{} {} call from {}.  Duration: {}'
                        ).format(
                            rec.status.capitalize(),
                            direction,
                            rec.calling_user.name,
                            rec.duration_human)
                    else:
                        message = _(
                            '{} {} call from {} to {}. Duration: {}'
                        ).format(
                            rec.status.capitalize(),
                            direction,
                            rec.calling_number,
                            rec.called_number,
                            rec.duration_human)
                    rec.ref.sudo().message_post(
                        subject=_('Call notification'),
                        body=message)
                    company_from = rec.ref
                    entities = []
                    if rec.ref.fields_get(['partner_id']).get('partner_id'):
                        entities.append(rec.ref.partner_id)
                        company_from = rec.ref.partner_id
                    if company_from.fields_get(['commercial_partner_id']).get(
                            'commercial_partner_id'):
                        entities.append(company_from.commercial_partner_id)
                    message += (''' - <a href="#" data-oe-model={}
                                    data-oe-id={}>{}</a>''').format(
                        rec.ref._name, rec.ref.id, rec.ref.name)
                    for entity in entities:
                        entity.sudo().message_post(
                            subject=_('Call notification'),
                            body=message)

                except Exception:
                    logger.exception('Register reference call error')
