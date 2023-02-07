###############################################################################
#
#    SDi Digital Group
#    Copyright (C) 2023-Today SDi Digital Group <www.sdi.es>
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
    'name': 'Vertical Base Installer',
    'summary': 'Addons for a base instance',
    'author': 'Jorge Quinteros, SDi Digital Group',
    'website': 'https://www.sdi.es/odoo-cloud/',
    'license': 'AGPL-3',
    'category': 'Vertical',
    'version': '15.0.1.0.0',
    'depends': [
        'disable_odoo_online',
        'mail_debrand',
        'mass_editing',
        'l10n_es',
        'l10n_es_partner',
        'l10n_es_toponyms',
        'remove_odoo_enterprise',
        'partner_contact_access_link',
        'web_advanced_search',
        'web_refresher',
        'web_no_bubble',
        'web_responsive',
        'web_tree_many2one_clickable',
    ],
    'application': True,
}
