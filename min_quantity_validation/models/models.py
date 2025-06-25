from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _check_min_qty(self):
        if not self.product_id or not self.product_uom_qty:
            return

        # جلب الحد الأدنى من stock.warehouse.orderpoint
        orderpoints = self.env['stock.warehouse.orderpoint'].search([
            ('product_id', '=', self.product_id.id)
        ], limit=1)  # يمكنك إزالتها لو عايز تتعامل مع أكثر من orderpoint

        if orderpoints and self.product_uom_qty < orderpoints.product_min_qty:
            return {
                'warning': {
                    'title': 'كمية أقل من الحد الأدنى',
                    'message': f"الكمية المطلوبة ({self.product_uom_qty}) أقل من الحد الأدنى ({orderpoints.product_min_qty}). هل تريد المتابعة؟",
                }
            }
