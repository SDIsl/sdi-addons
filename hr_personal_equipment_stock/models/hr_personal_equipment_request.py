# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrPersonalEquipmentRequest(models.Model):

    _inherit = "hr.personal.equipment.request"

    location_id = fields.Many2one(
        "stock.location",
        ondelete="cascade",
        required=True,
        domain=[("is_personal_equipment_location", "=", True)],
    )
    procurement_group_id = fields.Many2one(
        "procurement.group",
        "Procurement Group",
        help="Moves created through this stock request will be put in this "
        "procurement group. If none is given, the moves generated by "
        "procurement rules will be grouped into one big picking.",
        copy=False,
    )
    picking_ids = fields.One2many(
        "stock.picking", inverse_name="equipment_request_id")
    picking_count = fields.Integer(compute="_compute_picking_count")

    @api.depends("picking_ids")
    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)

    def _get_procurement_group(self):
        if self.procurement_group_id:
            return self.procurement_group_id.id
        return (
            self.env["procurement.group"].create(
                self._get_procurement_group_vals()).id
        )

    def _get_procurement_group_vals(self):
        return {
            "move_type": "direct",
            "equipment_request_id": self.id,
            "partner_id": self.employee_id.user_id.partner_id.id,
        }

    def _accept_request_vals(self):
        result = super()._accept_request_vals()
        result["procurement_group_id"] = self._get_procurement_group()
        return result

    def action_view_pickings(self):
        self.ensure_one()
        action = self.env.ref("stock.action_picking_tree_all").sudo().read()[0]
        action["domain"] = [("equipment_request_id", "=", self.id)]
        return action
