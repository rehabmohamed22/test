import logging
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
# this is used
class ZidCustomerSync(models.Model):
    _name = 'zid.customer.sync'
    _description = 'Zid Customer Sync'

    def action_sync_customers(self):
        config = self.env['zid.settings'].sudo().search([], limit=1)
        if not config:
            raise UserError("لم يتم العثور على إعدادات الربط مع زد.")

        headers = {
            "Authorization": f"Bearer {config.authorization}",
            "X-Manager-Token": config.access_token,
            "Accept-Language": "ar",
        }

        base_url = "https://api.zid.sa/v1/managers/store/customers"
        page = self.env['ir.config_parameter'].sudo().search([('key','=','zid_integration_customer')]).value
        page =int(page)
        per_page = 1000
        total_customers = 0

        params = {
            "page": page,
            "per_page": per_page,
        }

        response = requests.get(base_url, headers=headers, params=params)
        _logger.info(f"الاستجابة من API العملاء: {response.text}")

        if response.status_code != 200:
            raise UserError(f"فشل في جلب العملاء: {response.text}")

        data = response.json()
        customers = data.get("customers", [])



        for customer in customers:
            try:
                zid_id = customer.get('id')
                name = customer.get('name')
                email = customer.get('email')
                mobile = customer.get('mobile')

                _logger.info(f"معالجة العميل: {zid_id} - {name}")

                # تجاهل العملاء الذين ينقصهم الاسم أو رقم الهاتف
                if not name or not mobile:
                    _logger.warning(f"تم تجاهل العميل {zid_id} بسبب نقص البيانات.")
                    continue

                partner = self.env['res.partner'].search([('zid_customer_id', '=', zid_id)], limit=1)
                if partner:
                    partner.write({
                        'name': name,
                        'email': email,
                        'phone': mobile,
                    })
                else:
                    self.env['res.partner'].create({
                        'name': name,
                        'email': email,
                        'phone': mobile,
                        'zid_customer_id': zid_id,
                        'company_type': 'person',
                        'customer_rank': 1,  # يحدد أنه عميل
                    })

                total_customers += 1

            except Exception as e:
                _logger.error(f"فشل في حفظ العميل {customer}: {e}", exc_info=True)

        if len(customers)==1000:
            page += 1

        self.env['ir.config_parameter'].sudo().search([('key','=','zid_integration_customer')]).write({
            'value':str(page),
        })

        _logger.info(f"تم مزامنة {total_customers} عميل من زد.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'مزامنة العملاء',
                'message': f"تم مزامنة {total_customers} عميل بنجاح.",
                'type': 'success',
                'sticky': False,
            }
        }