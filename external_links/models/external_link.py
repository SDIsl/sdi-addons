###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models
from werkzeug import urls


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

    def _clean_website(self, website):
        url = urls.url_parse(website)
        if not url.scheme:
            if not url.netloc:
                url = url.replace(netloc=url.path, path='')
            website = url.replace(scheme='https').to_url()
        return website

    @api.model
    def create(self, vals):
        if vals.get('url'):
            vals['url'] = self._clean_website(vals['url'])
        return super().create(vals)

    def write(self, vals):
        if vals.get('url'):
            vals['url'] = self._clean_website(vals['url'])
        return super().write(vals)
