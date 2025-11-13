# -*- coding: utf-8 -*-
import base64
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import pytz
import logging

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

# --- helpers de fecha/horario compatibles ---
def _to_local_iso(env, dt):
    """Convierte str/datetime/None a 'YYYY-MM-DDTHH:MM:SS±HH:MM' en la tz del usuario."""
    if not dt:
        return u""
    if isinstance(dt, basestring):  # Py2/3: en Py3 basestring no existe, lo definimos abajo
        dt = fields.Datetime.from_string(dt)
    # Localizar si viene naive
    if getattr(dt, 'tzinfo', None) is None:
        dt = pytz.UTC.localize(dt)
    tzname = (env.context or {}).get('tz') or getattr(env.user, 'tz', None) or 'UTC'
    try:
        tz = pytz.timezone(tzname)
    except Exception:
        tz = pytz.UTC
    return dt.astimezone(tz).replace(microsecond=0).isoformat()

# Compat Py3: basestring
try:
    basestring
except NameError:  # Py3
    basestring = (str,)

class VerifactuEventExporter(object):
    def __init__(self, invoice):
        self.invoice = invoice

    def _post_to_chatter(self, body):
        """Compat de message_post para v10–v18."""
        inv = self.invoice
        try:
            subtype = inv.env.ref('mail.mt_comment')
            if subtype:
                return inv.message_post(body=body, subtype_id=subtype.id)
        except Exception:
            pass
        try:
            return inv.message_post(body=body, subtype='mail.mt_comment', message_type='comment')
        except Exception:
            return inv.message_post(body=body)

    def export(self):
        try:
            inv = self.invoice
            inv.ensure_one()

            events = inv.env["verifactu.event.log"].search(
                [('company_id', '=', inv.company_id.id)],
                order="timestamp asc"
            )

            xml_content = self._generate_event_xml(events)
            file_name = 'verifactu_events_%s.xml' % datetime.now().strftime("%Y%m%d_%H%M%S")

            # res_model dinámico (v10: account.invoice, v13+: account.move)
            res_model = inv._name

            # Odoo espera base64 como str (no bytes) en v10
            datas_b64 = base64.b64encode(xml_content.encode("utf-8"))
            try:
                datas_b64 = datas_b64.decode('ascii')  # Py3
            except Exception:
                pass  # Py2 ya es str

            attachment = inv.env["ir.attachment"].create({
                "name": file_name,
                "type": "binary",
                "res_model": res_model,
                "res_id": inv.id,
                "datas": datas_b64,
                "mimetype": "application/xml",
            })

            # Chatter + log (evita f-strings/emojis problemáticos en Py2)
            msg = _(u"Exportación de registros de eventos generados: %s") % file_name
            try:
                _logger.info(msg)
            except Exception:
                _logger.info(repr(msg))
            self._post_to_chatter(msg)

            return {
                "type": "ir.actions.act_url",
                "url": "/web/content/%s?download=true" % attachment.id,
                "target": "new",
            }

        except Exception as e:
            err = _("Error al exportar registros de eventos: %s") % (str(e),)
            try:
                self._post_to_chatter(err)
            except Exception:
                _logger.error(repr(err))
            raise UserError(err)

    def _generate_event_xml(self, events):
        root = ET.Element("Eventos")
        for event in events:
            evento_element = ET.SubElement(root, "Evento")
            ET.SubElement(evento_element, "Timestamp").text = _to_local_iso(self.invoice.env, event.timestamp)
            ET.SubElement(evento_element, "Mensaje").text = event.name or u""
        rough = ET.tostring(root, "utf-8")  # Py2 devuelve str; Py3 bytes
        # minidom.parseString admite bytes/str; estandarizamos a bytes
        if not isinstance(rough, (bytes, bytearray)):
            rough = rough.encode('utf-8')
        reparsed = minidom.parseString(rough)
        # Devuelve unicode; compatible Py2/3
        return reparsed.toprettyxml(indent="  ")
