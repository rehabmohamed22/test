import logging
import requests
import json
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ZidProductSync(models.Model):
    _name = 'zid.product.sync'
    _description = 'Zid Product Sync'

    def action_sync_products(self):
        config = self.env['zid.settings'].sudo().search([], limit=1)
        if not config:
            raise UserError("لم يتم العثور على إعدادات الربط مع زد.")

        headers = {
            "Authorization": f"Bearer {config.authorization}",
            "X-Manager-Token": config.access_token,
            "Accept-Language": "ar",
            "Store-Id": '40228',
            "Role": "Manager"
        }

        base_url = "https://api.zid.sa/v1/products"
        page = self.env['ir.config_parameter'].sudo().search([('key', '=', 'zid_integration_product')]).value
        page = int(page)
        per_page = 10
        total_products = 0

        params = {
            "page": page,
            "per_page": per_page,
        }

        response = requests.get(base_url, headers=headers, params=params)
        _logger.info(f"استجابة صفحة {page}: {response.text}")

        if response.status_code != 200:
            raise UserError(f"فشل في جلب المنتجات في الصفحة {page}: {response.text}")

        data = response.json()
        products = data.get("results", [])

        # if not products:
        #     break  # لا يوجد مزيد من المنتجات

        for product in products:
            try:
                zid_id = product.get("id")
                name = product.get("name", {}).get("ar", "")
                price = product.get("price")
                sku = product.get("sku")

                if not name:
                    _logger.warning(f"تجاهل المنتج {zid_id} لعدم وجود اسم.")
                    continue

                existing_product = self.env['product.product'].search([('zid_product_id', '=', zid_id)], limit=1)
                if existing_product:
                    existing_product.write({
                        'name': name,
                        'list_price': price,
                        'default_code': sku,
                    })
                else:
                    self.env['product.product'].create({
                        'name': name,
                        'list_price': price,
                        'default_code': sku,
                        'zid_product_id': zid_id,
                    })

                total_products += 1

            except Exception as e:
                _logger.error(f"خطأ أثناء مزامنة المنتج {product}: {e}", exc_info=True)

        if len(products) == 10:
            page += 1

        self.env['ir.config_parameter'].sudo().search([('key', '=', 'zid_integration_product')]).write({
            'value': str(page),
        })

        _logger.info(f"تم مزامنة {total_products} منتج من زد.")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'مزامنة المنتجات',
                'message': f"تم مزامنة {total_products} منتج بنجاح.",
                'type': 'success',
                'sticky': False,
            }
        }

