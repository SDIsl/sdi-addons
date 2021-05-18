###############################################################################
#
#    SDi Soluciones Digitales
#    Copyright (C) 2021-Today SDi Soluciones Informáticas <www.sdi.es>
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
    'name': 'Project Task Disable Auto Subscribe',
    'summary': '''Check on user for disabling auto subscription when the user
                  creates a new project task.''',
    'author': '''Valentín Castravete Georgian, Jorge Luis Quinteros,
                 SDi Soluciones Digitales''',
    'website': 'https://sdi.web.sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Project',
    'version': '12.0.1.0.0',
    'depends': [
        'project',
    ],
    'data': [
        'views/res_users.xml',
    ],
}
