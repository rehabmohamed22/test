from odoo import models, fields, api

class LabTestType(models.Model):
    _name = 'lab.test.type'
    _description = 'Laboratory Test Type'

    name = fields.Char(string='Test Name', required=True)
    reference_range = fields.Char(string='Reference Range')
    unit = fields.Char(string='Unit')
    price = fields.Float(string='Price', required=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        """عند إنشاء تحليل جديد، يتم إنشاء منتج مرتبط به تلقائيًا"""
        product = self.env['product.product'].create({
            'name': vals.get('name', 'New Lab Test'),
            'type': 'service',  # ✅ تحديده كخدمة
            'list_price': vals.get('price', 0.0),
            'invoice_policy': 'order',
        })
        vals['product_id'] = product.id
        return super(LabTestType, self).create(vals)
