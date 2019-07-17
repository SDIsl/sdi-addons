# SDI
# © 2018 Oscar Soto <osoto@sdi.es> <@oscars8a>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi: Modify No sale_order_line_sequence in Sale Report',
    'version': '11.0.1.0.1',
    'category': 'Sales',
    'summary': """
        Modify the OCA module sale_order_line_sequence for no put sequence in Sale Report """,
    'author': 'Oscar Soto',
    'license': 'AGPL-3',
    'depends': [
        'sale_order_line_sequence',
    ],
    'data': [
        'data/report_saleorder.xml'
    ],
    'installable': True,
    'application': False,
}
