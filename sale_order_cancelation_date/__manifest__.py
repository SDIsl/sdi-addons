###############################################################################
#
#    SDi Digital Group
#    Copyright (C) 2022-Today SDi Digital Group <www.sdi.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Sale Order Cancelation Date',
    'summary': 'Adds cancelation date on sales order',
    'author': 'Alberto Martínez, SDi Digital Group',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'license': 'AGPL-3',
    'category': 'Sales',
    'version': '12.0.1.0.0',
    'depends': [
        'sale'
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'post_init_hook': 'auto_complete_cancelation_date'
}
