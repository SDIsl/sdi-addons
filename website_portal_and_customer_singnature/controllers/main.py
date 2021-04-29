# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    @http.route(['/my/quotes/accept'], type='json', auth="public",
                website=True)
    def portal_quote_accept(self, res_id, access_token=None, partner_name=None,
                            signature=None):
        result = super(CustomerPortal, self).portal_quote_accept(
            res_id,
            access_token,
            partner_name,
            signature)
        if not result.get('error', False):
            res = request.env['sale.order'].browse(res_id)
            res.sudo().customer_signature = signature
        return result
