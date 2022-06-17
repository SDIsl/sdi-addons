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
    'name': 'Mail Template Delete Menu',
    'version': '14.0.1.0.0',
    'category': 'Mail',
    'summary': '''This module allows users to eliminate their mail templates
                from a menu.''',
    'author': 'Miguel Lucendo, SDi Digital Group',
    'license': 'AGPL-3',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'depends': [
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/mail_template_delete_menu_security.xml',
        'views/mail_template_views.xml',
    ],
}
