from odoo import models, fields, api

class SaleOrderLineWizard(models.TransientModel):
    _name = "sale.order.line.wizard"
    _description = "عرض تفاصيل سطر المبيعات"

    sale_order_line_id = fields.Many2one("sale.order.line", string="سطر أمر البيع", readonly=True)
    order_id = fields.Many2one("sale.order", string="أمر البيع", related="sale_order_line_id.order_id", readonly=True)
    partner_id = fields.Many2one("res.partner", string="العميل", related="order_id.partner_id", readonly=True)
    order_date = fields.Datetime("التاريخ", related="order_id.date_order", readonly=True)
    product_id = fields.Many2one("product.product", string="المنتج", related="sale_order_line_id.product_id", readonly=True)
    quantity = fields.Float("الكمية", related="sale_order_line_id.product_uom_qty", readonly=True)
    price = fields.Float("السعر", related="sale_order_line_id.price_unit", readonly=True)

    @api.model
    def default_get(self, fields_list):
        """تحضير القيم الافتراضية للـ Wizard"""
        defaults = super().default_get(fields_list)
        sale_order_line_id = self.env.context.get('default_sale_order_line_id')
        if sale_order_line_id:
            sale_line = self.env['sale.order.line'].browse(sale_order_line_id)
            defaults.update({
                'sale_order_line_id': sale_line.id,
            })
        return defaults
