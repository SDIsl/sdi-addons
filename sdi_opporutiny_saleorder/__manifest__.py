# SDI
# © 2018 Oscar Soto <osoto@sdi.es> <@oscars8a>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi-CRM: Add oportunity field in Sale Order',
    'version': '11.0.1.0.1',
    'category': 'Extra Tools',
    'summary': """
        Add oportunity field on the top of de order.""",
    'author': 'Oscar Soto',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'crm',
        'sale_management'
    ],
    'data': [
        'views/sale_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
