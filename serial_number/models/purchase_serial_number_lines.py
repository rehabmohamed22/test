from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sequence = fields.Integer(string="Serial", compute="_compute_sequence", store=True)

    @api.depends('order_id.order_line')
    def _compute_sequence(self):
        for order in self.mapped('order_id'):
            lines = order.order_line.sorted(key=lambda x: x.id or 0)  # حل مشكلة NewId
            for index, line in enumerate(lines, start=1):
                line.sequence = index
