# -*- coding: utf-8 -*-
{
    'name': "Account payment term extension propagate",

    'summary': """
        Makes holiday payment term for next year
        """,
    'author': "Sergio Lop <SDi Group>",
    'website': "https://www.sdi.es/odoo",
    'category': 'Payment',
    'version': '12.0.0.1',
    'depends': ['account_payment_term_extension'],
    'data': [
        'views/views.xml',
        'data/cron.xml',
    ],
}
