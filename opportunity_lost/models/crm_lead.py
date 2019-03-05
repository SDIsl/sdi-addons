# -*- coding: utf-8 -*-
# SDI
# © 2012-2015 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _


class Lead(models.Model):
    _inherit = 'crm.lead'

    lost_description = fields.Text(string=_("Lost Description"), track_visibility='onchange')

