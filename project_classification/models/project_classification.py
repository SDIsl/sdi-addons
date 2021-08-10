###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class ProjectClassification(models.Model):
    _name = 'project.classification'
    _description = 'Classification of projects'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Char(
        string='Description',
    )
    sequence = fields.Integer(
        'Sequence',
    )
