from datetime import datetime
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sequence = fields.Integer(string="Serial", compute="_compute_sequence", store=True, readonly=True)

    @api.depends('order_id.order_line')
    def _compute_sequence(self):
        for order in self.mapped('order_id'):
            lines = order.order_line.sorted(key=lambda x: x.create_date or datetime.min)
            for index, line in enumerate(lines, start=1):
                line.sequence = index