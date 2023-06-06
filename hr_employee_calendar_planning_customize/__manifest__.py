###############################################################################
#
#    SDi Soluciones Digitales
#    Copyright (C) 2022-Today SDi Soluciones Digitales <www.sdi.es>
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
    'name': 'Hr Employee Calendar Planning Customize',
    'summary': 'Custom modifications of calendar planning oca module',
    'author': '''Sergio Lop Sanz, 
    Miguel Lucendo Esteban, SDi Soluciones Digitales''',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'version': '12.0.1.1.0',
    'depends': [
        'hr_employee_calendar_planning',
        'sysadmin_base'
    ],
    'data': [
        'views/hr_employee_calendar_views.xml',
        'views/hr_employee_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
