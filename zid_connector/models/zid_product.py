from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)

class ZidProduct(models.Model):
    _name = 'zid.product'
    _description = 'Zid Product'
    _rec_name = 'name'

    name = fields.Char(string="Product Name")
    zid_product_id = fields.Char(string="Zid Product ID")
    price = fields.Float(string="Price")
    sku = fields.Char(string="SKU")
    stock_quantity = fields.Integer(string="Stock Quantity")
    product_view_id = fields.Many2one('zid.product.view', string="Product View")


class ZidProductView(models.Model):
    _name = 'zid.product.view'
    _description = 'Zid Product View'

    product_ids = fields.One2many('zid.product', 'product_view_id', string="Products")
    store_id = fields.Char(string="Store ID", required=True)

    def action_fetch_products(self):
        self.ensure_one()
        if not self.id:
            raise UserError("من فضلك احفظ السجل أولاً قبل جلب المنتجات.")

        config = self.env['zid.settings'].sudo().search([], limit=1)
        if not config:
            raise UserError("لا يوجد إعدادات Zid حالياً.")

        access_token = config.access_token
        authorization = config.authorization
        store_id = self.store_id

        headers = {
            "Accept-Language": "en",
            "Authorization": f"Bearer {authorization}",
            "X-Manager-Token": access_token,
            "Store-Id": store_id,
            "Role": "Manager"
        }

        self.product_ids.unlink()

        page = 1
        page_size = 50
        fetched_any = False

        while True:
            url = f"https://api.zid.sa/v1/products/?page={page}&page_size={page_size}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise UserError(_("فشل في جلب المنتجات: %s") % response.text)

            data = response.json()
            _logger.info("Zid Products Response: %s", data)

            items = data.get("results", [])

            if not items:
                _logger.warning("No products found in response.")
                if not fetched_any:
                    raise UserError("لا يوجد منتجات حالياً على منصة زد.")
                break

            fetched_any = True

            for item in items:
                self.env['zid.product'].sudo().create({
                    "name": item.get("name"),
                    "zid_product_id": item.get("id"),
                    "price": item.get("price", {}).get("amount", 0) if isinstance(item.get("price"), dict) else item.get("price", 0),
                    "sku": item.get("sku"),
                    "stock_quantity": item.get("stock", {}).get("quantity", 0),
                    "product_view_id": self.id
                })

            if len(items) < page_size:
                break

            page += 1

        # ✅ عرض رسالة نجاح
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تم بنجاح',
                'message': 'تم جلب المنتجات من منصة زد بنجاح ✅',
                'type': 'success',
                'sticky': False,
            }
        }
