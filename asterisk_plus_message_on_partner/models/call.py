
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
                    partner = rec.ref.partner_id
                    if partner:
                        message += (''' - <a href="#" data-oe-model={}
                                        data-oe-id={}>{}</a>''').format(
                            rec.ref._name, rec.ref.id, rec.ref.name)
                        partner.sudo().message_post(
                            subject=_('Call notification'),
                            body=message)
                except Exception:
                    logger.exception('Register reference call error')
