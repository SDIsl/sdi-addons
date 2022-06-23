from odoo import fields, models


class ProjectType(models.Model):
    _inherit = 'project.type'

    showBanner = fields.Boolean(string="Show Warning Banner")
