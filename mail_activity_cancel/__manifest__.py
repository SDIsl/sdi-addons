###############################################################################
#
#    SDi, Soluciones Informáticas
#    Copyright (C) 2019-Today Sistemas Digitales de Informática <www.sdi.es>
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
    'name': 'Mail Activity Cancel',
    'license': 'LGPL-3',
    'summary': 'leave a note as a comment when canceling an activity',
    'author': 'Jorge Luis Quinteros',
    'category': 'Mail',
    'version': '12.0.1.0.1',
    'depends': [
        'mail',
    ],
    'data': [
        'views/templates.xml',
        'views/message_activity_cancel.xml',
    ],
    'qweb': [
        'static/src/xml/mail_activity_item.xml',
    ],
}
