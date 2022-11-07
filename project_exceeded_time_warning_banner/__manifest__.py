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
    'name': 'Project Exceeded Time Warning Banner',
    'summary': '''If project has a negative balance
         and project type has Show Warning Banner option set as True,
         a warning message will be shown in projects and tasks.''',
    'author': 'Darío Sanz, SDi Soluciones Digitales',
    'website': 'https://sdi.web.sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Project',
    'version': '12.0.1.0.0',
    'depends': [
        'project',
        'hr_timesheet_balance',
        'project_category',
    ],
    'data': [
        'views/edit_project.xml',
        'views/view_task_form2.xml',
        'views/settings.xml',
        'views/project_type_form.xml',
    ],
}
