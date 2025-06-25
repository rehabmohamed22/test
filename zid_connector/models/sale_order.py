from odoo import models, fields, api
from .zid_api import ZidAPIService
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    zid_order_id=fields.Char(string="Order Number")


    def action_sync_zid_order_status(self):
        for order in self:
            zid_api = ZidAPIService(
                access_token='ryC62GQEoHENF67IGcWVdsBl61xxPAvNEGYbw2JY',  # أو خليها تيجي من إعدادات config
                manager_token='توكن مدير المتجر هنا'
            )
            result = zid_api.update_order_status(
                order_id=order.zid_order_id,
                status='ready',  # أو حسب الحالة عندك
                inventory_address_id='معرف المستودع'
            )
            _logger.info("تم تحديث الطلب في زد: %s", result)



# def write(self, vals):
    #     # نطبق الخصم على السطور اللي تم تغيير السعر فيها
    #     for line in self:
    #         updated_vals = vals.copy()  # نعمل نسخة علشان ما نعدلش في الأصل
    #         if 'price_unit' in vals or 'price_after_discount' in vals or 'product_uom_qty' in vals:
    #             if 'price_unit' not in updated_vals:
    #                 updated_vals['price_unit'] = line.price_unit
    #             if 'price_after_discount' not in updated_vals:
    #                 updated_vals['price_after_discount'] = line.price_after_discount
    #             if 'product_uom_qty' not in updated_vals:
    #                 updated_vals['product_uom_qty'] = line.product_uom_qty
    #             self._compute_discount(updated_vals)
    #             line.update(updated_vals)
    #             return True
    #     return super(SaleOrderLine, self).write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_after_discount=fields.Float(string="Price After Discount")

    # @api.model
    # def create(self, vals):
    #     res = super(SaleOrderLine, self).create(vals)
    #     print("EEEEEEEEEEE")
    #     price_unit = vals.get('price_unit')
    #     price_after_discount = vals.get('price_after_discount')
    #
    #     if price_unit and price_after_discount and price_unit > 0:
    #         discount = (1 - (price_after_discount / price_unit)) * 100
    #         print(discount)
    #         vals['discount'] = discount
    #
    #     return res
