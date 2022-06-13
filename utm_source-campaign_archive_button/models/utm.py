# -*- coding: utf-8 -*-
from odoo import models, fields


class UtmSource(models.Model):
    _inherit = 'utm.source'
    active = fields.Boolean(string='Active', default=True)


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'
    active = fields.Boolean(string='Active', default=True)
