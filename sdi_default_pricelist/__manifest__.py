# SDI
# © 2019 Oscar Soto <osoto@sdi.es> <@oscars8a>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi-Sale: Set a default rate',
    'version': '11.0.1.0.1',
    'category': 'Sale',
    'summary': """
          This module puts in the first position in the list at the top of
          the rate list by default.""",
    'author': 'Oscar Soto',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'sale_management',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
}
