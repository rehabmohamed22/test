import logging
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ZidOrderFetcher(models.Model):
    _name = 'zid.order.fetcher'
    _description = 'Zid Orders Fetcher'

    order_item_ids = fields.One2many('zid.order.item', 'fetcher_id', string="كل المنتجات")
    order_ids = fields.One2many('zid.order', 'fetcher_id', string="Orders")

    def action_fetch_orders(self):
        config = self.env['zid.settings'].sudo().search([], limit=1)
        if not config:
            raise UserError("لا يوجد إعدادات Zid.")

        headers = {
            "Authorization": f"Bearer {config.authorization}",
            "X-Manager-Token": config.access_token,
            "Accept-Language": "ar"
        }

        # إضافة معلمة per_page لتحديد عدد النتائج المسترجعة
        params = {
            'per_page': 50,  # تحديد 50 طلب فقط
        }

        url = "https://api.zid.sa/v1/managers/store/orders"

        # إرسال الطلب إلى الـ API
        response = requests.get(url, headers=headers, params=params)

        # طباعة الاستجابة الكاملة للتحقق من البيانات
        _logger.info(f"استجابة API: {response.text}")  # طباعة الاستجابة الكاملة من API

        if response.status_code != 200:
            raise UserError(f"فشل في جلب الطلبات من زد. الكود: {response.status_code}\nالنص: {response.text}")

        orders = response.json().get('orders', [])
        if not orders:
            _logger.info("لا توجد طلبات في الصفحة 1.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'جلب الطلبات',
                    'message': 'لا توجد طلبات.',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        self.order_ids.unlink()  # حذف الطلبات القديمة المرتبطة بهذا السطر فقط
        _logger.info("قبل إضافة الطلبات")

        for order in orders:
            order_rec = self.env['zid.order'].create({
                'fetcher_id': self.id,
                'zid_order_id': order.get('id'),
                'customer_name': order.get('customer_name'),
                'payment_status': order.get('payment_status'),
                'created_at': order.get('created_at'),
            })

            for item in order.get('items', []):
                self.env['zid.order.item'].create({
                    'order_id': order_rec.id,
                    'product_name': item.get('product_name'),
                    'quantity': item.get('quantity'),
                    'price': item.get('price'),
                    'fetcher_id': self.id
                })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تم الجلب بنجاح',
                'message': f"تم جلب {len(orders)} طلب بنجاح.",
                'type': 'success',
                'sticky': False,
            }
        }


class ZidOrder(models.Model):
    _name = 'zid.order'
    _description = 'Zid Order'

    fetcher_id = fields.Many2one('zid.order.fetcher', string="أداة الجلب")
    zid_order_id = fields.Char(string="Order Id", required=True)
    customer_name = fields.Char(string="Customer Name")
    payment_status = fields.Selection([
        ('paid', 'paid'),
        ('unpaid', 'unpaid'),
        ('pending', 'pending'),
    ], string="Payment Status")
    created_at = fields.Datetime(string="Date of Creation")

    item_ids = fields.One2many('zid.order.item', 'order_id', string="Products")


class ZidOrderItem(models.Model):
    _name = 'zid.order.item'
    _description = 'Zid Order Item'

    order_id = fields.Many2one('zid.order', string="Orders", ondelete='cascade')
    product_name = fields.Char(string="Product Name")
    quantity = fields.Integer(string="Amount")
    price = fields.Float(string="Price")
    fetcher_id = fields.Many2one('zid.order.fetcher', string="اللي جلب الطلب")
