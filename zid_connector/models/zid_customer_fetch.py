# models/zid_customer_fetch.py
from odoo import models, fields, api
from odoo.exceptions import UserError
import requests


class ZidCustomerFetch(models.Model):  # TransientModel لأنها شاشة مؤقتة
    _name = 'zid.customer.fetch'
    _description = 'Zid Fetch Customer By ID'

    zid_customer_id = fields.Char(string="Zid Customer ID", required=True)
    name = fields.Char(string="Name")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender")
    created_at = fields.Datetime(string="Created At")

    def action_fetch_customer(self):
        settings = self.env['zid.settings'].search([], limit=1)
        if not settings or not settings.access_token:
            raise UserError("Access token not found in zid.settings")

        url = f"https://api.zid.sa/v1/managers/store/customers/{self.zid_customer_id}"
        access_token = settings.access_token
        authorization = settings.authorization

        headers = {
            "Authorization": f"Bearer {authorization}",
            "X-Manager-Token": access_token,
            "Accept-Language": "ar"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise UserError(f"API Error: {response.text}")

        data = response.json().get("data", {})
        self.name = data.get("name")
        self.email = data.get("email")
        self.phone = data.get("phone")
        self.gender = data.get("gender")
        self.created_at = data.get("created_at")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Zid Customer',
            'res_model': 'zid.customer.fetch',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
