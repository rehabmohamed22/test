from odoo import models, fields

class StockScrapLine(models.Model):
    _name = 'stock.scrap.line'
    _description = 'Scrap Line'

    temp_scrap_id = fields.Many2one('stock.scrap', string="Temporary Scrap")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    description = fields.Text(string="Description")
    scrap_id = fields.Many2one('stock.scrap', string="Scrap")
