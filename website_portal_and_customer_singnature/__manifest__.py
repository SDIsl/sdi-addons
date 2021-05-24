# © 2019 SDi Soluciones Informáticas
# Author: Oscar Soto <osoto@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi-Website: Website portal_signature in cutomer_signature',
    'version': '11.0.1.0.1',
    'category': 'Website',
    'summary': """
        Put the website quotation signature in customer_signature sale.order
         field""",
    'author': 'Oscar Soto',
    'license': 'AGPL-3',
    "website": "http://www.sdi.es",
    'depends': [
        'sale',
        'sale_order_digitized_signature',
    ],
    'installable': True,
    'application': False,
}
