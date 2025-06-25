from odoo import models, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty')
    def _check_stock_quantity(self):
        if self.product_id:
            available_stock = self.product_id.qty_available

            if self.product_uom_qty > available_stock:
                raise UserError(
                    f"The requested quantity for the product '{self.product_id.name}' is greater than the available stock of {available_stock}. Please enter a valid quantity."
                )
