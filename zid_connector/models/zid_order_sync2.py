from odoo import models, fields
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class ZidOrderSync(models.Model):
    _name = 'zid.order.sync'
    _description = 'Zid Order Synchronization Manager'

    name = fields.Char(string="Sync Title", default="Zid Order Manager")

    zid_order_id = fields.Char(string="Zid Order ID")
    zid_order_status = fields.Selection([
        ('new', 'new'),
        ('preparing', 'preparing'),
        ('ready', 'ready'),
        ('indelivery', 'indelivery'),
        ('delivered', 'delivered'),
        ('cancelled', 'cancelled'),
    ], string="Zid Order Status")


    def action_update_status(self):
        _logger.info("🔄 جاري تحديث حالة الطلب...")

        # جلب التوكن من جدول الإعدادات
        config = self.env['zid.settings'].sudo().search([], limit=1)
        access_token = config.access_token
        authorization =config.authorization

        print("access_token repr:", repr(access_token))

        if not access_token:
            raise ValueError("❌ لا يوجد access token. برجاء التأكد من الربط أولاً.")

        if not self.zid_order_id or not self.zid_order_status:
            raise ValueError("⚠️ من فضلك أدخل رقم الطلب واختر الحالة.")

        url = f"https://api.zid.sa/v1/managers/store/orders/{self.zid_order_id}/change-order-status"

        headers = {
            "Authorization": f"Bearer {authorization}",
            "X-Manager-Token": access_token,
            "Accept-Language": "ar"
        }

        # تجهيز البيانات بصيغة form-data
        data = {
            "order_status": self.zid_order_status,
        }


        # إرسال الطلب بصيغة multipart/form-data
        response = requests.post(url, headers=headers, data=data)

        _logger.info(f"✅ Response Status: {response.status_code}")
        _logger.info(f"📦 Response Body: {response.text}")
        print("Status:", response.status_code)
        print("Body:", response.text[:500])

        if response.status_code == 200:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "تم التحديث",
                    'message': "✅ تم تحديث حالة الطلب بنجاح!",
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "فشل التحديث",
                    'message': f"⚠️ لم يتم التحديث. الرد من زد: {response.text}",
                    'type': 'danger',
                    'sticky': True,
                }
            }