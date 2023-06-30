###############################################################################
#
#    SDi Digital Group
#    Copyright (C) 2023-Today SDi Digital Group https://www.sdi.es/odoo-cloud/
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
    'name': 'Partner Disable VAT Check Option',
    'version': '14.0.1.0.0',
    'summary': 'Creates a new option to disable the VAT check on partners.',
    'author': 'Valentín Georgian Castravete, SDi Digital Group',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'license': 'AGPL-3',
    'category': 'Custom',
    'depends': ['base_vat'],
    'data': ['views/res_config_settings_views.xml'],
}
