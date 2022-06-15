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
    'name': 'CRM Lead Related Directory',
    'version': '14.0.1.0.0',
    'category': 'Customer Relationship Management',
    'summary': '''This module adds the possibility to create a related
                    directory to a lead and adds a \'link\' to it.''',
    'author': 'Miguel Lucendo, SDi Digital Group',
    'license': 'AGPL-3',
    'website': 'http://www.sdi.es',
    'depends': [
        'crm',
        'dms',
    ],
    'data': [
        'views/crm_lead_views.xml',
        'views/dms_directory_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
