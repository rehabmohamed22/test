from odoo import models, fields

class ScrapOrderMulti(models.Model):
    _name = 'scrap.order.multi'
    _description = 'Scrap Order with Multiple Products'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('scrap.order.multi'), required=True)
    date = fields.Datetime(default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    location_id = fields.Many2one('stock.location', string='Scrap Location', required=True)
    line_ids = fields.One2many('scrap.order.multi.line', 'order_id', string='Scrap Lines')

    def action_validate(self):
        for line in self.line_ids:
            self.env['stock.scrap'].create({
                'product_id': line.product_id.id,
                'product_uom_id': line.product_id.uom_id.id,
                'scrap_qty': line.quantity,
                'location_id': self.location_id.id,
                'company_id': self.company_id.id,
                'origin': self.name,
            })

class ScrapOrderMultiLine(models.Model):
    _name = 'scrap.order.multi.line'
    _description = 'Scrap Order Line'

    order_id = fields.Many2one('scrap.order.multi', required=True)
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(required=True, default=1.0)
