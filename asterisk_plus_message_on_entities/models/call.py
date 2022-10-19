
import logging
from odoo import models, api, _

logger = logging.getLogger(__name__)


class Call(models.Model):
    _inherit = 'asterisk_plus.call'

    @api.constrains('is_active')
    def register_call(self):
        self.ensure_one()
        for rec in self:
            if rec.is_active or not rec.ref:
                continue
            try:
                if not rec.partner and rec.ref.partner_id:
                    rec.sudo().write({'partner': rec.ref.partner_id.id})
                if rec.direction == 'out':
                    if rec.status == 'noanswer':
                        start_msg = _('No answer outgoing call')
                    elif rec.status == 'answered':
                        start_msg = _('Answered outgoing call')
                    elif rec.status == 'busy':
                        start_msg = _('Busy outgoing call')
                    elif rec.status == 'failed':
                        start_msg = _('Failed outgoing call')
                    else:
                        start_msg = _('In progress outgoing call')
                else:
                    if rec.status == 'noanswer':
                        start_msg = _('No answer incoming call')
                    elif rec.status == 'answered':
                        start_msg = _('Answered incoming call')
                    elif rec.status == 'busy':
                        start_msg = _('Busy incoming call')
                    elif rec.status == 'failed':
                        start_msg = _('Failed incoming call')
                    else:
                        start_msg = _('In progress incoming call')
                message = start_msg
                message_partner = start_msg
                from_msg = ' ' + _('from') + ' {}'
                from_msg_num = ' ({})'.format(rec.calling_number)
                to_msg = ' ' + _('to') + ' {}'
                to_msg_num = ' ({})'.format(rec.called_number)
                partner_ref = ('''<a href="#" data-oe-model={}
                                    data-oe-id={}>{}</a>''').format(
                    rec.partner._name, rec.partner.id,
                    rec.partner.name) if rec.partner else ''
                if rec.called_user:
                    if rec.partner:
                        message += from_msg.format(partner_ref) + from_msg_num
                    else:
                        message += from_msg.format(rec.calling_number)
                    message_partner += from_msg.format(rec.calling_number)
                    message += to_msg.format(
                        rec.called_user.name) + to_msg_num
                    message_partner += to_msg.format(
                        rec.called_user.name) + to_msg_num
                elif rec.calling_user:
                    message += from_msg.format(rec.calling_user.name) + \
                        from_msg_num
                    message_partner += from_msg.format(
                        rec.calling_user.name) + from_msg_num
                    if rec.partner:
                        message += to_msg.format(partner_ref) + to_msg_num
                    else:
                        message += to_msg.format(rec.called_number)
                    message_partner += to_msg.format(rec.called_number)
                else:
                    message += from_msg.format(rec.calling_number)
                    message += to_msg.format(rec.called_number)
                    message_partner += from_msg.format(rec.calling_number)
                    message_partner += to_msg.format(rec.called_number)
                end_msg = ('. ' + _('Duration') + ': {}').format(
                    rec.duration_human)
                message += end_msg
                message_partner += end_msg
                entities = [rec.ref]
                if rec.partner and rec.partner != rec.ref:
                    entities.append(rec.partner)
                if rec.partner and rec.partner.fields_get([
                        'commercial_partner_id']).get('commercial_partner_id'):
                    if rec.partner.commercial_partner_id != rec.ref:
                        entities.append(rec.partner.commercial_partner_id)
                entity_name = self.env['ir.translation'].search([
                    ('source', '=', rec.ref._description),
                    ('lang', '=', 'es_ES'),
                    ('state', '=', 'translated'),
                ], limit=1)
                entity_name = entity_name.value if entity_name else \
                    rec.ref._description
                message_to_company = message
                entity_ref = ('''<br>{} - <a href="#" data-oe-model={}
                                data-oe-id={}>{}</a>''').format(
                    entity_name, rec.ref._name, rec.ref.id, rec.ref.name)
                for entity in entities:
                    if rec.partner and rec.partner == entity:
                        msg_to_send = message_partner + \
                            (entity_ref if rec.partner != rec.ref else '')
                    elif rec.partner and rec.partner.commercial_partner_id == \
                            entity:
                        msg_to_send = message_to_company if rec.ref == \
                            rec.partner else (message + entity_ref)
                    else:
                        msg_to_send = message + (entity_ref if entity !=
                                                 rec.ref else '')
                    entity.sudo().message_post(
                        subject=_('Call notification'),
                        body=msg_to_send)
            except Exception:
                logger.exception(_('Register reference call error.'))

    @api.constrains('is_active')
    def register_reference_call(self):
        pass
