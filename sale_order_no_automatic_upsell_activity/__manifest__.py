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
    'name': 'Sale Order No Automatic Upsell Activity',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'summary': '''This module stops odoo from creating automatic activity
                 when an upsell can be done.''',
    'author': 'Miguel Lucendo, SDi Digital Group',
    'license': 'AGPL-3',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'depends': [
        'sale',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
}
