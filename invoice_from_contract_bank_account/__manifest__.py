# -*- coding: utf-8 -*-
{
    'name': "Invoice from contract bank account",

    'summary': """
        When payment mode is bank transfer in contracts, invoices from
        contract must indicates bank account to make transfer""",
    'author': "Sergio Lop Sanz <<SDi Group>>",
    'website': "https://www.sdi.es/odoo",
    'category': 'sales',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['contract',
                'l10n_es_facturae',
                ],
}
