from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "Sale Order Line Inherit"

    index = fields.Integer(
        compute='_compute_line_index'
    )

    @api.depends('order_id.order_line')
    def _compute_line_index(self):
        for idx, record in enumerate(self.order_id.order_line):
            record.index = idx + 1
