###############################################################################
#
#    Sidoo Soluciones S.L.
#    Copyright (C) 2023-Today SDi Sidoo Soluciones S.L. <www.sidoo.es>
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
    'name': 'CRM Lead Stage',
    'summary': 'This module adds stages in the leads.',
    'author': 'Jorge Quinteros, Sidoo Soluciones S.L.',
    'website': 'https://sidoo.es',
    'license': 'AGPL-3',
    'category': 'CRM',
    'version': '16.0.1.0.0',
    'depends': [
        'crm',
        'sale_crm',
    ],
    'data': [
        'views/crm_lead_stage_views.xml',
        'views/crm_lead_views.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
}
