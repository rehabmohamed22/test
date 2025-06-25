from odoo import models, fields, api


class ImagingTestType(models.Model):
    _name = 'lab.imaging.type'
    _description = 'Imaging Test Type'

    name = fields.Char(string='Imaging Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)

    @api.model
    def create(self, vals):
        """عند إنشاء أشعة جديدة، يتم إنشاء منتج مرتبط بها تلقائيًا"""
        product = self.env['product.product'].create({
            'name': vals.get('name', 'New Imaging Test'),
            'type': 'service',  # ✅ تحديده كخدمة
            'list_price': vals.get('price', 0.0),
            'invoice_policy': 'order',
        })
        vals['product_id'] = product.id
        return super(LabImagingType, self).create(vals)


