###############################################################################
#
#    SDi, Soluciones Digitales
#    Copyright (C) 2020-Today, SDi, Soluciones Digitales
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
    'name': 'project_task_title_strikethrough',
    'summary': 'Tittle line through in task when is in stage closed',
    'category': 'Project',
    'version': '12.0.1.0.1',
    'author': 'Jorge Luis Quinteros, Imanol Ruiz',
    'website': 'https://www.sdi.es/odoo/',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'project_stage_closed',
    ],
    'data': [
        'views/tasks_templates.xml',
        'views/tasks_views.xml',
    ],
}
