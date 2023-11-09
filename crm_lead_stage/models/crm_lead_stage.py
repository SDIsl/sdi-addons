###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import fields, models


class LeadStage(models.Model):
    _name = 'crm.lead.stage'
    _description = 'CRM Lead Stage'

    name = fields.Char(
        string='Nombre',
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=1,
        help='Se usa para ordenar las etapas de las iniciativas. Más bajo es mejor.',
    )

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.name + ' (Copia)'
        return super().copy(default)
