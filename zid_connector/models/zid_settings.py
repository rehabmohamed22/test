from odoo import models, fields,api
import logging
import requests
from odoo.exceptions import UserError
from urllib.parse import quote

_logger = logging.getLogger(__name__)

class ZidSettings(models.Model):
    _name = 'zid.settings'
    _description = 'Zid Settings'

    name = fields.Char(default='Zid Configuration')
    client_id = fields.Char(string='Client ID', required=True)
    client_secret = fields.Char(string='Client Secret', required=True)
    access_token = fields.Char(string='Access Token')
    authorization = fields.Char(string='Authorization')
    refresh_token = fields.Char(string='Refresh Token')

    def action_connect(self):
        base_url = "https://4583-154-236-119-130.ngrok-free.app"
        redirect_uri = f"{base_url}/zid/callback"

        # تحقق من وجود القيم المطلوبة
        if not self.client_id or not self.client_secret:
            raise UserError("من فضلك ادخل Client ID و Client Secret قبل المتابعة.")

        # سكوب الصلاحيات
        scope = (
            "zid:categories.read zid:categories.write "
            "zid:customers.read zid:customers.write "
            "zid:orders.read zid:orders.write "
            "zid:coupons.read zid:coupons.write "
            "zid:delivery_options.read zid:delivery_options.write "
            "zid:products.read zid:products.write "
            "zid:webhooks.read zid:webhooks.write "
            "zid:catalog.read zid:catalog.write "
            "zid:subscriptions.read zid:subscriptions.write "
            "zid:inventory.read zid:inventory.write "
            "zid:extra_addons.read zid:extra_addons.write "
            "zid:order_create.write "
            "zid:product_inventory_stock.read zid:product_inventory_stock.write "
            "zid:embedded_apps.read zid:embedded_apps.write "
            "zid:loyalty.read zid:loyalty.write "
            "zid:reverse_orders.read zid:reverse_orders.write "
            "zid:product_availability_notifications.read zid:product_availability_notifications.write "
            "zid:account.read zid:vats.read zid:abandoned_carts.read zid:payments.read "
            "zid:countries.read zid:cities.read "
            "zid:bundle_offers.read"
        )

        # ترميز السكوب
        encoded_scope = quote(scope)

        # بناء الرابط النهائي
        url = (
            f"https://oauth.zid.sa/oauth/authorize?"
            f"client_id={self.client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={encoded_scope}&"
            f"prompt=consent"
        )

        # لو عايز تتأكد اطبع الرابط في اللوج
        print("🔗 Authorization URL:", url)

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

    # @api.model
    # def refresh_zid_token(self):
    #     config = self.search([], limit=1)
    #     if not config or not config.refresh_token:
    #         _logger.error("لا يوجد إعدادات زد أو  you must refresh_token")
    #         return False
    #
    #     payload = {
    #         'grant_type': 'refresh_token',
    #         'client_id': config.client_id,
    #         'client_secret': config.client_secret,
    #         'refresh_token': config.refresh_token,
    #     }
    #
    #     try:
    #         response = requests.post("https://oauth.zid.sa/oauth/token", data=payload)
    #         data = response.json()
    #
    #         if 'access_token' in data:
    #             config.write({
    #                 'access_token': data.get('access_token'),
    #                 'refresh_token': data.get('refresh_token'),
    #             })
    #             _logger.info("تم تجديد access_token بنجاح.")
    #         else:
    #             _logger.error(f"فشل التجديد: {data}")
    #     except Exception as e:
    #         _logger.error(f"حدث خطأ أثناء تجديد التوكن: {str(e)}")
