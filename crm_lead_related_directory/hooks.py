###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    admin_group = env['dms.access.group'].search([('name', '=', 'Admin')])
    env['dms.directory'].create(vals_list={
        'name': 'Leads',
        'is_root_directory': True,
        'storage_id': 1,
        'is_hidden': False,
        'complete_group_ids': [(4, admin_group.id)],
    })
