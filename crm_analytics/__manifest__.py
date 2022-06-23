###############################################################################
#
#    SDi Soluciones Informáticas
#    Copyright (C) 2022-Today SDi Soluciones Informáticas <www.sdi.es>
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
    'name': 'CRM Analytics',
    'version': '14.0.1.0.1',
    'category': 'Customer Relationship Management',
    'summary': 'Module for monitoring stage change in an opportunity.',
    'author': 'Oscar Soto, Darío Sanz, SDi Soluciones Digitales',
    'license': 'AGPL-3',
    'website': 'https://sdi.web.sdi.es/odoo/',
    'depends': [
        'sale_crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/move.xml',
        'views/stage.xml',
        'views/lead.xml',
    ],
}
