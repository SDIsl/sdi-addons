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
    'name': 'Project Form Access Link',
    'summary': '''Allow you to click on a button and open the full project 
                  form while watching project kanban view.''',
    'author': 'Valentín Georgian Castravete, SDi Soluciones Digitales',
    'website': 'https://sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Project',
    'version': '12.0.1.0.1',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_views.xml',
    ],
}
