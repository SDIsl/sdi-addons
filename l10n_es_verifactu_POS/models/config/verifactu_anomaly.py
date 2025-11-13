# models/verifactu_anomaly.py (v12)

from odoo import models, fields, api, _

class VerifactuAnomaly(models.Model):
    _name = "verifactu.anomaly"
    _description = "Anomalías VeriFactu detectadas"
    _order = "detected_at desc, id desc"

    company_id = fields.Many2one('res.company', string="Compañía", required=True, index=True)
    move_id = fields.Many2one('account.invoice', string="Factura", required=True, index=True)

    # NUEVOS (compat con tu helper):
    code = fields.Char(string="Código", index=True)
    detected_by = fields.Many2one('res.users', string="Detectada por")

    anomaly_type = fields.Selection([
        ('stale_pending', "Pendiente estancada"),
        ('out_of_order', "Desorden cronológico"),
        ('generic', "Genérica"),  # <-- para LIC/CFG/REQ u otras
    ], string="Tipo", required=True, index=True)

    severity = fields.Selection([
        ('info', 'Info'),
        ('warning', 'Aviso'),
        ('error', 'Error'),
    ], string="Severidad", default='warning', required=True)

    message = fields.Text(string="Descripción", required=True)
    detected_at = fields.Datetime(string="Detectada", required=True, default=fields.Datetime.now)
    resolved = fields.Boolean(string="Resuelta", default=False, index=True)
    resolved_at = fields.Datetime(string="Fecha de resolución")

    move_name = fields.Char(related="move_id.number", string="Número", store=False)
    invoice_date = fields.Date(related="move_id.date_invoice", string="Fecha factura", store=False)
    verifactu_status = fields.Char(string="Estado VF actual", compute="_compute_vf_status", store=False)

    @api.depends('move_id')
    def _compute_vf_status(self):
        for rec in self:
            rec.verifactu_status = getattr(rec.move_id, 'verifactu_status', '') or ''

    _sql_constraints = [
        ('uniq_open_per_move_type',
         'unique(move_id, anomaly_type, resolved)',
         "Ya existe una anomalía abierta de este tipo para la factura."),
    ]

    @api.multi
    def action_mark_resolved(self):
        for rec in self:
            if not rec.resolved:
                rec.write({'resolved': True, 'resolved_at': fields.Datetime.now()})
