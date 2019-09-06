# © 2019 SDi Soluciones
# Oscar Soto <osoto@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "SDi-Sale: Pack UOM Management",
    'version': '11.0.2.0.1',
    'category': '',
    'author': 'Oscar Soto, Sergio Lop',
    'summary': """
        Manage Packs like a uom. Add columns Box - Units of Box, Price Unit - Price /UnitBox""",
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'sdi_stock_picking_report_valued',
        'account_invoice_production_lot',
    ],
    'data': [
        'report/report_saleorder_templates.xml',
        'report/report_deliveryslip_templates.xml',
        'report/report_invoice_templates.xml',
        'report/report_stockpicking_templates.xml',
        'views/product.xml'
    ],
    'installable': True,
}
