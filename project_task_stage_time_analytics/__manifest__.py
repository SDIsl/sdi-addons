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
    'name': 'Project Task Stage Time Analytics',
    'version': '14.0.1.0.0',
    'category': 'Project',
    'summary': 'Module for monitoring status change in a project task. The '
            'time passed on each stage it\'s measured on natural days.',
    'author': 'Valentín Castravete, Miguel Lucendo, SDi Digital Group',
    'license': 'AGPL-3',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'depends': [
        'project',
        'project_status',
        'project_template',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/move.xml',
        'views/project_task.xml',
        'views/stage.xml',
    ],
}
