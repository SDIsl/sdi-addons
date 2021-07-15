###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ExternalLink(models.Model):
    _name = 'external.link'
    _description = 'Links to external sites.'

    name = fields.Char(
        string='Name',
        required=True,
    )
    url = fields.Char(
        string='URL',
        required=True,
    )
    external_link_group_id = fields.Many2one(
        comodel_name='external.link.group',
        string='External Link Group',
        required=True,
    )
