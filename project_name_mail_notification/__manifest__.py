###############################################################################
#
#    SDi Digital Group
#    Copyright (C) 2022-Today SDi Digital Group <www.sdi.es>
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
    'name': 'Project Name Mail Notification',
    'summary': '''It shows the proyect name in email task notification and in
        the Conversation project task messages.''',
    'author': '''Darío Sanz, Miguel Lucendo, Valentín Castravete Georgian,
        SDi Digital Group''',
    'website': 'https://sdi.web.sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Discuss',
    'version': '12.0.1.0.0',
    'depends': [
        'mail',
        'project'
    ],
    'data': [
        'views/assets.xml'
    ],
    'qweb': [
        'static/src/xml/thread.xml',
    ]
}
