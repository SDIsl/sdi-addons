from odoo import models, fields


class IRDeletionLog(models.Model):
    _name = 'ir.deletion.log'
    _description = 'IR Deletion Log'

    deletion_id = fields.Many2one(
        'ir.deletion',
        string='Deletion',
        required=True,
        ondelete='cascade')

    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    initial_count = fields.Integer(string='Initial Count', readonly=True)
    final_count = fields.Integer(string='Final Count', readonly=True)
