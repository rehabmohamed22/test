from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # partner_commission = fields.Float(string="Partner Commission (%)", readonly=True)
    
    @api.model
    def create(self, vals):
        order = self.env['sale.order'].browse(vals.get('order_id'))
        product = self.env['product.product'].browse(vals.get('product_id'))
        if order and product and order.partner_id:
            vals['discount'] = order.partner_id.discount or 0.0
        return super().create(vals)

    def write(self, vals):
        if 'product_id' in vals or 'order_id' in vals:
            for line in self:
                partner = line.order_id.partner_id
                product = vals.get('product_id') or line.product_id.id
                if partner and product:
                    vals['discount'] = partner.discount or 0.0
        return super().write(vals)

    # @api.onchange('product_id')
    # def _onchange_product_id_apply_discount(self):
    #     for line in self:
    #         if line.order_id.partner_id and line.product_id:
    #             commission = line.order_id.partner_id.discount or 0.0
    #             print(commission)
    #             line.discount = commission

