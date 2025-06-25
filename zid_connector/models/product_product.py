from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.template'

    zid_product_price = fields.Float(string='Zid Product Price')
