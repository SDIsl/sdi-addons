###############################################################################
#
#    SDi Soluciones Digitales
#    Copyright (C) 2021-Today SDi Soluciones Digitales <www.sdi.es>
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
    'name': 'Resource Management',
    'summary': 'It permits to associate resources and resource bookings to'
               ' employees.',
    'author': 'Valentín Castravete Georgian, SDi Soluciones Digitales',
    'website': 'https://sdi.web.sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Resources',
    'version': '12.0.1.0.0',
    'depends': [
        'hr',
        'product',
    ],
    'data': [
        'data/data.xml',
        'security/resource_management_security.xml',
        'security/ir.model.access.csv',
        'views/expendable_resource.xml',
        'views/hr_employee_views.xml',
        'views/product_views.xml',
        'views/resource_booking_management_views.xml',
        'views/resource_management_menu_views.xml',
    ],
    'qweb': [
        "static/src/xml/web_calendar.xml",
    ],
    'application': True,
}
