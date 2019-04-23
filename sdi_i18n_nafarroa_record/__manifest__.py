# SDI
# © 2018 Oscar Soto <osoto@sdi.es> <@oscars8a>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi [i18n] Modificación de nombre record Navarra',
    'version': '11.0.1.0.1',
    'category': 'Extra Tools',
    'summary': """
        Modificar record de base.state_es_na (nombre actual "Navarra (Nafarroa)", por, "Navarra") """,
    'author': 'Oscar Soto',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'l10n_es_toponyms',
    ],
    'data': [
        'data/res_country.xml'
    ],
    'installable': True,
    'application': False,
}

