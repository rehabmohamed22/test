from odoo import models, fields
import requests
from odoo.exceptions import UserError

class ZidCustomer(models.Model):
        _name = 'zid.customer'
        _description = 'Zid Customers'

        name = fields.Char("Name")
        email = fields.Char("Email")
        mobile = fields.Char("Mobile")
        nickname = fields.Char("Nickname")
        order_counts = fields.Integer("Total Orders")
        pivot_mobile = fields.Char("Pivot Mobile")
        pivot_email = fields.Char("Pivot Email")
        city = fields.Char("City")
        view_id = fields.Many2one('zid.customer.view', string="Display View")


class ZidCustomerView(models.Model):
    _name = 'zid.customer.view'
    _description = 'Zid Customer Display View'

    customer_ids = fields.One2many('zid.customer', 'view_id', string="Zid Customers")

    def fetch_zid_customers(self):
        config = self.env['zid.settings'].sudo().search([], limit=1)
        if not config:
            raise UserError("لا يوجد إعدادات Zid حالياً.")

        access_token = config.access_token
        authorization = config.authorization

        headers = {
            "Authorization": f"Bearer {authorization}",
            "X-Manager-Token": access_token,
            "Accept-Language": "ar"
        }

        url = "https://api.zid.sa/v1/managers/store/customers?page=1&per_page=20"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            customers = data.get("customers", [])

            if not customers:
                raise UserError("لا يوجد عملاء حالياً على منصة زد.")

            # حذف العملاء السابقين المرتبطين بنفس السجل
            self.customer_ids.unlink()

            for cust in customers:
                self.customer_ids.create({
                    "name": cust.get("name"),
                    "email": cust.get("email"),
                    "mobile": cust.get("mobile"),
                    "nickname": cust.get("nickname"),
                    "order_counts": cust.get("order_counts"),
                    "pivot_mobile": cust.get("pivotMobile"),
                    "pivot_email": cust.get("pivotEmail"),
                    "city": cust.get("city", {}).get("name"),
                    "view_id": self.id,
                })

        else:
            raise UserError(f"فشل في جلب العملاء. الكود: {response.status_code}")
