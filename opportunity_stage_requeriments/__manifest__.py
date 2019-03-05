# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "SDi-CRM: opportunity stages requeriments",
    'version': '11.0.1.0.1',
    'category': 'Extra Tools',
    'author': 'David Juaneda',
    'summary': """  
        Add requirements to configure opportunity states.""",
    'license': 'AGPL-3',
    'depends': [
        'crm',
    ],
    'data':[
        'views/inherit_crm_stage_form.xml',
    ],
    'installable':True,
}
