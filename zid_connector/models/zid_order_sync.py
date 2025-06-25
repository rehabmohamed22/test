# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging
import time
from datetime import datetime
import json

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_zid_order_id = fields.Char(string='Zid Order ID', copy=False, index=True)
    x_zid_source = fields.Char(string='Zid Order Source')
    x_zid_status = fields.Char(string='Zid Order Status')
    from_zid = fields.Boolean(string="From Zid")
    payment_type = fields.Char(string="Payment Method")
    @api.model
    def cron_fetch_zid_orders(self):
        print("Enter")
        config = self.env['zid.settings'].sudo().search([], limit=1)
        if not config:
            raise UserError("لم يتم العثور على إعدادات الربط مع زد.")
        print("After Config")
        headers = {
            "Authorization": f"Bearer {config.authorization}",
            "X-Manager-Token": config.access_token,
            "Accept-Language": "ar",
        }
        print("111111111")
        page = self.env['ir.config_parameter'].sudo().search([('key', '=', 'zid_integration_order')]).value
        page = int(page)
        per_page = 80
        print("222222222")
        base_url = "https://api.zid.sa/v1/managers/store/orders"
        params = {
            "page": page,
            "per_page": per_page
        }
        print("3333333333")
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            raise UserError(f"فشل في جلب الطلبات في الصفحة {page}: {response.text}")
        print("4444444444")
        orders = response.json().get('orders', [])
        if not orders:
            return
        for order in orders:
            print("5555555555555")

            zid_order_id = order.get('id')

            if not zid_order_id:
                continue

            if self.env['sale.order'].search_count([('zid_order_id', '=', str(zid_order_id))]):
                continue

            detail_url = f'https://api.zid.sa/v1/managers/store/orders/{zid_order_id}/view'
            detail_response = requests.get(detail_url, headers=headers, timeout=10)
            attempt = 0
            while attempt < 3:
                try:
                    detail_response = requests.get(detail_url, headers=headers, timeout=10)
                except requests.exceptions.RequestException as e:
                    time.sleep(2)
                    attempt += 1
                    continue

                if detail_response.status_code == 200:
                    break
                else:
                    time.sleep(2)
                    attempt += 1

            if detail_response.status_code != 200:
                continue

            json_data = detail_response.json()
            order_data = json_data.get('order', {})
            order_date_str = self.env['ir.config_parameter'].sudo().get_param('zid_order_date')
            created_at_str = order_data.get("created_at")  # مثال: "2025-05-12T14:37:19Z"

            order_date = datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
            created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")

            if created_at < order_date:
                continue
            customer_email = order_data.get('customer', {}).get('email')
            customer = self.env['res.partner'].search([('email', '=', customer_email)], limit=1)
            if not customer:
                continue
            payments = order_data.get('payment', [])
            method = payments.get('method')
            code = method.get('code')
            products = order_data.get('products', [])
            if not products:
                continue

            order_line = []
            for product in products:

                product_name = product.get('name')

                product_rec = self.env['product.product'].search([('name', '=', product_name)], limit=1)
                price_after_discount = product.get('price_with_additions')
                if product_rec:
                    order_line.append((0, 0, {
                        'product_id': product_rec.id,
                        'price_unit': product_rec.list_price,
                        'price_after_discount':price_after_discount,
                        'product_uom_qty': product.get('quantity')
                    }))
                else:
                    _logger.warning(f"المنتج غير موجود: {product_name}")

            new_order = self.create({
                'partner_id': customer.id,
                'zid_order_id': str(zid_order_id),
                'payment_type': str(code),
                'from_zid':True,
                'order_line': order_line,
            })
            for line in new_order.order_line:
                if line.price_unit:
                    discount = ((line.price_unit - line.price_after_discount) / line.price_unit) * 100
                    line.write({'discount': discount})
            new_order.action_confirm()
            for picking in new_order.picking_ids:
                if picking.state != 'cancel':
                    for move_line in picking.move_ids_without_package:
                        move_line.quantity = move_line.product_uom_qty
                    picking._autoconfirm_picking()
                    picking.button_validate()
                    picking._action_done()

            if not new_order.invoice_ids:
                new_order._create_invoices()
            invoice = new_order.invoice_ids.filtered(lambda inv: inv.state == 'draft')
            invoice.action_post()
        if len(orders) == 80:
            page += 1
        self.env['ir.config_parameter'].sudo().search([('key', '=', 'zid_integration_order')]).write({
            'value': str(page),
        })

        _logger.info(f"تم تحديث الصفحة إلى {page}")