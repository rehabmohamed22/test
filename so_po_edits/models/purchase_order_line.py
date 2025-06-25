from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    _description = "Purchase Order Line Inherit"

    index = fields.Integer(
        compute='_compute_line_index'
    )

    @api.depends('order_id.order_line')
    def _compute_line_index(self):
        for idx, record in enumerate(self.order_id.order_line):
            record.index = idx + 1
