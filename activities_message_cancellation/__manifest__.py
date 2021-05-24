# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi-CRM: message cancellation activity',
    "version": "11.0.1.0.1",
    'category': '',
    'author': 'David Juaneda',
    'summary': """
        Add log to canceled activity.""",
    'license': 'AGPL-3',
    'depends': [
        'crm',
    ],
    'data': [
        'views/crm_sdi_templates.xml',
        'views/mail_templates.xml',
    ],
    'qweb': [
        'static/src/xml/inherit_mail_activity_item.xml',
    ],
    'installable': True,
}
