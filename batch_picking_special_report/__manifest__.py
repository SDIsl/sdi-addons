# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Hoja de carga',
    'summary': 'Grupo de albaranes organizado por categoria, producto y lote',
    'version': '11.0.1.0.0',
    'author': "SDi, "
              "Odoo Community Association (OCA)",
    'development_status': 'Beta',
    'maintainers': [
        'SDi',
    ],
    'category': 'Inventory',
    'depends': [
        'stock_batch_picking',
    ],
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'data': [
        'report/hoja_de_carga.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
