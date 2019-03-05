# SDI
# © 2018 Oscar Soto <osoto@sdi.es> <@oscars8a>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi [IMP] Añadir Widgets gplaces en form res.partner',
    'version': '11.0.1.0.1',
    'category': 'Location',
    'summary': """
        Añadir los widgets gplaces_address_autocomplete en el campo zip_id (Location Complete) y name en el form de res.partner """,
    'author': 'Oscar Soto',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web_google_maps'
    ],
    'data': [
        'views/inherit_res_partner.xml'
    ],
    'installable': True,
    'application': False,
}