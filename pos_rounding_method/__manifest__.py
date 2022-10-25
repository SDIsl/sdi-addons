###############################################################################
#
#    SDi Digital Group
#    Copyright (C) 2020-Today SDi Digital Group <www.sdi.es>
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
    'name': 'Pos Rounding Method',
    'summary': '''Adds a rounding method parameter on the POS configuration to
        apply it in the POS orders.''',
    'author': 'Valentín Castravete, Jorge Quinteros, SDi Digital Group',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'license': 'AGPL-3',
    'category': 'Point Of Sale',
    'version': '12.0.1.0.0',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/assets.xml',
        'views/res_config_settings_views.xml',
    ],
}
