from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    scrap_line_ids = fields.One2many('stock.scrap.line', 'scrap_id', string='Scrap Lines')
    product_id = fields.Many2one('product.product', string="Product", required=False)
    product_uom_id = fields.Many2one('uom.uom', string="UoM", required=False)
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('converted', 'Converted'),
    # ], default='draft', string="Status")

    def action_validate(self):
        new_scraps = self.env['stock.scrap']

        for rec in self:
            for line in rec.scrap_line_ids:
                if not line.product_id or line.quantity <= 0:
                    raise ValidationError("Each scrap line must have a product and quantity greater than 0.")

                scrap = self.env['stock.scrap'].create({
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_id.uom_id.id,
                    'scrap_qty': line.quantity,
                    'location_id': rec.location_id.id,
                    'scrap_location_id': rec.scrap_location_id.id,
                    'company_id': rec.company_id.id,
                })
                scrap.action_validate()
                new_scraps |= scrap  # اجمعهم في recordset واحد

        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated Scraps',
            'res_model': 'stock.scrap',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', new_scraps.ids)],
            'target': 'current',
        }

    # def action_validate(self):
    #     for rec in self:
    #         if not rec.scrap_line_ids:
    #             raise ValidationError("Please add at least one scrap line.")
    #
    #         for line in rec.scrap_line_ids:
    #             if not line.product_id or not line.quantity:
    #                 raise ValidationError("Each scrap line must have a product and quantity.")
    #
    #             self.env['stock.scrap'].create({
    #                 'product_id': line.product_id.id,
    #                 'product_uom_id': line.product_id.uom_id.id,
    #                 'scrap_qty': line.quantity,
    #                 'location_id': rec.location_id.id,
    #                 'scrap_location_id': rec.scrap_location_id.id,
    #                 'company_id': rec.company_id.id,
    #             }).action_validate()
    #
    #         rec.unlink()
    #     return {'type': 'ir.actions.act_window_close'}

    def button_confirm_and_validate(self):
        self.ensure_one()
        self = self.sudo().browse(self.id)  # إعادة تحميل بعد الحفظ
        self.env.cr.commit()  # إجبار الحفظ قبل القراءة
        return self.action_validate()

    @api.model
    def create(self, vals):
        if not vals.get('product_id') and vals.get('scrap_line_ids'):
            for line_data in vals['scrap_line_ids']:
                line_vals = line_data[2]
                if line_vals and line_vals.get('product_id') and line_vals.get('quantity', 0) > 0:
                    product = self.env['product.product'].browse(line_vals['product_id'])
                    vals.update({
                        'product_id': line_vals['product_id'],
                        'product_uom_id': product.uom_id.id,
                        'scrap_qty': line_vals['quantity'],
                    })
                    break  # استخدمنا أول سطر صحيح فقط
        return super().create(vals)
