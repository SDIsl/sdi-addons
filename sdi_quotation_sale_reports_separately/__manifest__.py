# © 2019 SDi Soluciones
# Oscar Soto <osoto@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "SDi-Sale: Quotation and Sale Reports separately",
    'version': '11.0.1.0.1',
    'category': '',
    'author': 'Oscar Soto',
    'summary': """
        Add Quotation and Sale Order Reports separately and Mail templates.""",
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'data/order_mail_template.xml',
        'data/quotation_mail_template.xml',
        'report/order_report_template.xml',
        'report/quotation_report_template.xml',
        'report/sale_report.xml',
    ],
    'installable': True,
}
