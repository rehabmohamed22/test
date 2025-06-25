# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PriceList(models.Model):
    _inherit = 'product.pricelist.item'

    category_id = fields.Many2one('uom.category',related='product_tmpl_id.uom_id.category_id')
    uom_id = fields.Many2one('uom.uom',domain="[('category_id','=',category_id)]")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'order_id.pricelist_id')
    def _compute_price_unit(self):
        for line in self:
            # لو مفيش منتج أو Pricelist بلاش نحسب حاجة
            if not line.product_id or not line.order_id.pricelist_id:
                continue

            # فلترة عناصر الـ Pricelist المناسبة
            matching_items = line.order_id.pricelist_id.item_ids.filtered(
                lambda item: ((not item.product_tmpl_id or item.product_tmpl_id == line.product_id.product_tmpl_id)
                    and (not item.uom_id or item.uom_id == line.product_uom)
                )
            )

            # لو لقيت عنصر مناسب بالسعر، خده
            if matching_items:
                line.price_unit = matching_items[0].fixed_price
            else:
                # fallback للسعر العادي من النظام لو مفيش عنصر مناسب
                line.price_unit = line.product_id.with_context(pricelist=line.order_id.pricelist_id.id,uom=line.product_uom.id).list_price
