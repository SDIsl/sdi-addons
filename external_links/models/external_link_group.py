###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ExternalLinkGroup(models.Model):
    _name = 'external.link.group'
    _description = 'Group of External Links.'

    name = fields.Char(
        string='Name',
        required=True,
    )
    external_link_ids = fields.One2many(
        comodel_name='external.link',
        inverse_name='external_link_group_id',
        string='External Links',
    )
