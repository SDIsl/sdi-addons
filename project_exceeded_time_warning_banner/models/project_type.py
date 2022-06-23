from odoo import fields, models


class ProjectType(models.Model):
    _inherit = 'project.type'

    show_banner = fields.Boolean(string="Show Warning Banner")
