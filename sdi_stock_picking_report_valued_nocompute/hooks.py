# Copyright 2020 Sergio Lop Sanz <slop@sdi.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry, vals=None):
    """For brand new installations"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    valores = env['stock.picking'].search([
        ('state', '=', 'done'),
        ('picking_type_id', '=', 1),
        ('amount_total', '=', 0),
        ('sale_id', '>', 0)
    ])
    for item in valores:
        item.valued_calculation()
