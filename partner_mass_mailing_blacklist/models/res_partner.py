###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def add_email_blacklist(self):
        blacklist_model = self.env['mail.blacklist']
        for record in self:
            blacklist_model._add(record.email)

    def remove_email_blacklist(self):
        blacklist_model = self.env['mail.blacklist']
        for record in self:
            blacklist_model._remove(record.email)
