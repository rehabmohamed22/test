from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_low_stock = fields.Boolean(string="Low Stock", store=True)
    # color = fields.Integer(string="Color", store=True)

    def update_product_stock_color(self):
        """ تحديث لون المنتج بناءً على المخزون في stock.quant """
        StockQuant = self.env['stock.quant']
        for product in self.search([]):  # البحث عن جميع المنتجات
            total_qty = sum(StockQuant.search([('product_id', '=', product.id)]).mapped('quantity'))
            product.is_low_stock = total_qty <= 10  # تحديد المنتجات منخفضة المخزون
    print(is_low_stock)
