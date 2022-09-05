# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class MismatchedTaxesReport(models.Model):
    _name = "mismatched.tax.report"
    _description = "Mismatched taxes report"
    _auto = False

    move_id = fields.Many2one(
        comodel_name='account.move'
    )
    move_line_id = fields.Many2one(
        comodel_name='account.move.line'
    )
    move_company_id = fields.Many2one(
        comodel_name='res.company'
    )
    wrong_company_id = fields.Many2one(
        comodel_name='res.company'
    )
    date = fields.Date(
        related="move_line_id.date"
    )
    type = fields.Selection(
        [
            ('TAX', 'Tax'),
            ('ACC', 'Account'),
            ],
        string="Type of incident"
    )

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT
            aml.id as id,
            am.id as move_id,
            aml.id as move_line_id,
            aml.company_id as move_company_id,
            ata.company_id as wrong_company_id,
            'TAX' as type
        FROM account_move am
            JOIN account_move_line aml on aml.move_id = am.id
            JOIN account_tax ata on ata.id = aml.tax_line_id
        WHERE aml.company_id != ata.company_id
                           UNION
        SELECT
            aml.id as id,
            am.id as move_id,
            aml.id as move_line_id,
            aml.company_id as move_company_id,
            acc.company_id as wrong_company_id,
            'ACC' as type
        FROM account_move am
            JOIN account_move_line aml on aml.move_id = am.id
            JOIN account_account acc on acc.id = aml.account_id
        WHERE aml.company_id != acc.company_id
        )""" % self._table)
