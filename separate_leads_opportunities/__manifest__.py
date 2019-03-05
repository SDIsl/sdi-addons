# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "SDi-CRM: separete leads and opportunies",
    'version': '11.0.1.0.1',
    'category': 'Extra Tools',
    'author': 'David Juaneda',
    'summary': """
        Separate activities from leads or opportunities.""",
    'license': 'AGPL-3',
    'depends': [
        'crm',
    ],
    'data':[
       'views/crm_sdi_templates.xml',
    ],
    'qweb': [
        'static/src/xml/inherit_client_action.xml',
        'static/src/xml/inherit_systray.xml',
     ],
    'installable':True,
}
