# -*- coding: utf-8 -*-
{
    'name': "group_validation",

    'summary': """
        Creación de un grupo para dar permisos de creación sobre las oportunidades""",

    'description': """
        Creación de un grupo para dar permisos de creación sobre las oportunidades
    """,

    'author': "Imanol Ruiz",
    'website': "http://www.SDI.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/iniciativa_security.xml',
        #'views/templates.xml'

    ],
}