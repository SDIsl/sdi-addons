###############################################################################
#
#    SDi Soluciones Digitales
#    Copyright (C) 2020-Today SDi Soluciones Digitales <www.sdi.es>
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
    'name': 'CRM Lead Group Permits',
    'summary': 'Create a group to edit CRM. Only this group can edit',
    'author': 'Imanol Ruiz, SDi Soluciones Digitales',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'category': 'Customer Relationship Management',
    'version': '12.0.1.0.0',
    'depends': [
        'crm',
    ],
    'data': [
        'security/group_permits_security.xml',
        'security/ir.model.access.csv',
    ],
}
