# -*- coding: utf-8 -*-
import os

from odoo import http
from odoo.http import request
from odoo_rpc_client import Client
import xmlrpc.client
import requests
import logging
import json
import datetime
import base64
from datetime import date
from odoo import fields

_logger = logging.getLogger(__name__)


class SokiaAuth(http.Controller):

    def set_test_app_domains(self):
        """
        This method to get the current server data
        :return: dict of the server data {'db','url_domain','ip','admin_login','admin_pass'}
        """
        settings = http.request.env['res.config.settings'].sudo().get_values()
        return {
            'db': settings['p_db'],
            'url_domain': settings['p_domain'],
            'ip': settings['p_ip'],
            'admin_login': settings['p_admin_user'],
            'admin_pass': settings['p_admin_pass']
        }

    @http.route('/sokia/get_domain', type='json', auth="public", methods=['POST'])
    def get_domain_work(self, **kw):
        """{
            "params":{
                "db": "test" or "live"
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('db'):
            return {'status_code': 200, 'is_error': True, "message": "Please enter your DB.", 'result_rpo': ''}

        settings = http.request.env['res.config.settings'].sudo().get_values()
        if kw.get('db') == 'test':
            data = {
                'domain': settings['t_domain'] or "",
                'ip': settings['t_ip'] or ""
            }
            return {'status_code': 200, 'is_error': False, 'message': 'done', 'result': data}
        else:
            data = {
                'domain': settings['p_domain'] or "",
                'ip': settings['p_ip'] or ""
            }
            return {'status_code': 200, 'is_error': False, 'message': 'done', 'result': data}

    def product_data(self, product):
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        base_path = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        image_url = ""
        item = request.env['product.product'].sudo().search([('id', '=', product)])
        if item.product_tmpl_id.attachment_id.local_url:
            item.product_tmpl_id.attachment_id.public = True
            image_url = base_path + item.product_tmpl_id.attachment_id.local_url

        return image_url

    def product_tmpl_data(self, product):
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        base_path = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        image_url = ""
        item = request.env['product.template'].sudo().search([('id', '=', product)])
        if item.attachment_id.local_url:
            item.attachment_id.public = True
            image_url = base_path + item.attachment_id.local_url

        return image_url

    def customer_attach(self, customer):
        base_path = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        image_url = []
        attachments = request.env["ir.attachment"].sudo().search([('res_id', '=', customer)])
        attachments.sudo().write({
            'public': True
        })
        for attach in attachments:
            if attach.local_url:
                image_url.append(base_path + attach.local_url)
        return image_url

    # @http.route('/sokia/customer_images/<int:customer>', methods=['POST', 'GET'], csrf=False, type='http', auth="public", website=True)
    # def customer_attach(self, customer=False):
    #     # base_path = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
    #     image_url = []
    #     attachments = request.env["ir.attachment"].sudo().search([('res_id', '=', customer)])
    #     attachments.sudo().write({
    #         'public': True
    #     })
    #     for attach in attachments:
    #         if attach.local_url:
    #             image_url.append(self.url_domain + attach.local_url)
    #     return {'images': image_url}

    @http.route('/sokia/login', type='json', auth="public", methods=['POST'])
    def authenticate_user(self, **kw):
        """{
            "params":{
                "email": "",
                "password": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('email'):
            return {'status_code': 200, 'is_error': True, "message": "Please enter your email.", 'result_rpo': ''}
        if not kw.get('password'):
            return {'status_code': 200, 'is_error': True, "message": "Please enter your password.", 'result_rpo': ''}

        login = kw.get('email')
        password = kw.get('password')

        try:
            client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], login, password)
            # client = Client(self.url, self.database, login, password)
            user = client['res.users'].search([('login', '=', login)])
            user_data = client['res.users'].read(user, ['name', 'login'])
            user_data_list = json.loads(json.dumps(user_data))
            return {'status_code': 200, 'is_error': False, 'message': 'done', 'user': user_data_list}
        except:
            return {'status_code': 200, 'is_error': True, "message": "Invalid credentials."}

    @http.route('/sokia/change_password', type='json', auth="public", methods=['POST'])
    def change_password(self, **kw):
        """{
            "params":{
                "email": "",
                "old_password": "",
                "new_password": "",
                "confirm_password": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('email'):
            return {'status_code': 200, 'is_error': True, "message": "Please enter your email.", 'result_rpo': ''}
        if not kw.get('old_password'):
            return {'status_code': 200, 'is_error': True, "message": "Please enter your current password.", 'result_rpo': ''}
        if not kw.get('new_password'):
            return {'status_code': 200, 'is_error': True, "message": "Please enter new password.", 'result_rpo': ''}
        if not kw.get('confirm_password'):
            return {'status_code': 200, 'is_error': True, "message": "Please confirm password.", 'result_rpo': ''}
        if kw.get('new_password') != kw.get('confirm_password'):
            return {'status_code': 200, 'is_error': True, "message": "New password is not equal confirm password.", 'result_rpo': ''}

        login = kw.get('email')
        old_password = kw.get('old_password')
        new_password = kw.get('new_password')

        try:
            client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], login, old_password)
            # client = Client(self.url, self.database, login, old_password)
            user = client['res.users'].search([('login', '=', login)])
            vals = {'password': new_password}
            admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
            # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
            admin_client['res.users'].write([user[0]], vals)

            return {'status_code': 200, 'is_error': False, 'message': 'Password changed successfully'}
        except:
            return {'status_code': 200, 'is_error': True, "message": "Please enter a valid password.", 'result_rpo': ''}

    @http.route('/sokia/get_pricelist', type='json', auth="public", methods=['POST'])
    def get_pricelist(self, **kw):
        """{
            "params":{
                "salesperson_id": ""
            }
        }"""

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        price_lists = admin_client['product.pricelist'].search([])
        price_lists_data = admin_client['product.pricelist'].read(price_lists, ['id', 'name'])
        price_lists_data_list = json.loads(json.dumps(price_lists_data))

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': price_lists_data_list}

    @http.route('/sokia/customers', type='json', auth="public", methods=['POST'])
    def get_customers(self, **kw):
        """{
            "params":{
                "salesperson_id": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, "message": "Cannot get all customers, please specify salesperson to get his customers.", 'result_rpo': ''}

        user_id = int(kw.get('salesperson_id'))
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        customers = admin_client['res.partner'].search([('user_id', '=', user_id)])
        customer_data = admin_client['res.partner'].read(customers, ['name', 'street', 'company_type',
                                                                     'property_account_receivable_id'])

        customer_data_list = json.loads(json.dumps(customer_data))

        for line in customer_data_list:
            invoices = admin_client['account.move'].search([('type', '=', 'out_invoice'), ('state', '=', 'posted'),
                                                            ('partner_id', '=', line['id'])])
            invoices_data = admin_client['account.move'].read(invoices, ['amount_total'])
            invoice_data_list = json.loads(json.dumps(invoices_data))

            totals = 0.00
            for total in invoice_data_list:
                totals += total['amount_total']

            line['total'] = round(totals, 2)

            if not line['street']:
                line['street'] = ""
            if not line['company_type']:
                line['company_type'] = ""
            if not line['property_account_receivable_id']:
                line['property_account_receivable_id'] = []

            # partner = admin_client['res.partner'].search([('id', '=', opportunity['partner_id'][0])])
            # partner_data = admin_client['res.partner'].read(partner, ['property_account_receivable_id'])
            # partner_data_list = json.loads(json.dumps(partner_data))

            items = admin_client['account.move.line'].search([('partner_id', '=', line['id']),
                                                              ('parent_state', '=', 'posted'),
                                                              ('account_id', '=',
                                                               line['property_account_receivable_id'][0])])
            items_data = admin_client['account.move.line'].read(items, ['debit', 'credit'])
            items_data_list = json.loads(json.dumps(items_data))

            balance = 0.00
            for l in items_data_list:
                balance += l['debit']
                balance -= l['credit']

            line['balance'] = balance
            if balance == 0.0:
                line['status'] = "no amount due"
            else:
                line['status'] = "has amount due %s" % balance

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': customer_data_list}

    @http.route('/sokia/customer_data', type='json', auth="public", methods=['POST'])
    def get_customer_data(self, **kw):
        """{
            "params":{
                "customer_id": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('customer_id'):
            return {'status_code': 200, 'is_error': True, "message": "Cannot get all customers, please specify salesperson to get his customers.", 'result_rpo': ''}

        customer_id = int(kw.get('customer_id'))
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        customers = admin_client['res.partner'].search([('id', '=', customer_id)])
        customer_data = admin_client['res.partner'].read(customers, ['name', 'street', 'parent_id', 'email', 'vat',
                                                                     'registry_num', 'mobile', 'company_type',
                                                                     'property_product_pricelist', 'partner_longitude',
                                                                     'partner_latitude', 'is_location_exception'])
        customer_data[0]['images'] = self.customer_attach(customer_id)
        # customer_data[0]['images'] = '%s/sokia/customer_images/%s' % (self.url_domain, customer_id)

        customer_data_list = json.loads(json.dumps(customer_data))

        if not customer_data[0]['street']:
            customer_data[0]['street'] = ""
        if not customer_data[0]['parent_id']:
            customer_data[0]['parent_id'] = []
        if not customer_data[0]['email']:
            customer_data[0]['email'] = ""
        if not customer_data[0]['vat']:
            customer_data[0]['vat'] = ""
        if not customer_data[0]['registry_num']:
            customer_data[0]['registry_num'] = ""
        if not customer_data[0]['mobile']:
            customer_data[0]['mobile'] = ""
        if not customer_data[0]['company_type']:
            customer_data[0]['company_type'] = ""
        if not customer_data[0]['property_product_pricelist']:
            customer_data[0]['property_product_pricelist'] = []

        return {'status_code': 200, 'is_error': False, "message": 'done', 'result_rpo': customer_data_list}

    @http.route('/sokia/edit_customer_location', type='json', auth="public", methods=['POST'])
    def edit_customer_location(self, **kw):
        """{
            "params":{
                "customer_id": "",
                "long": "",
                "lat": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('customer_id'):
            return {'status_code': 200, 'is_error': True,
                    "message": "Cannot get data, please specify customer_id to get his data.",
                    'result_rpo': ''}
        if not kw.get('long'):
            return {'status_code': 200, 'is_error': True,
                    "message": "Cannot get update location, please specify long/lat to able to update it.",
                    'result_rpo': ''}
        if not kw.get('lat'):
            return {'status_code': 200, 'is_error': True,
                    "message": "Cannot get update location, please specify long/lat to able to update it.",
                    'result_rpo': ''}

        customer = request.env['res.partner'].sudo().search([('id', '=', int(kw.get('customer_id')))])
        if customer.partner_longitude != 0 or customer.partner_latitude != 0:
            return {'status_code': 200, 'is_error': True,
                    "message": "You Are Unable to Edit the Customer Location, Please Contact your Supervisor.",
                    'result_rpo': ''}
        updated_customer = customer.sudo().write({
            'partner_longitude': float(kw.get('long')),
            'partner_latitude': float(kw.get('lat')),
        })

        # customer_id = int(kw.get('customer_id'))
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        # customers = admin_client['res.partner'].search([('id', '=', customer_id)])
        # customer_data = admin_client['res.partner'].read(customers, ['name', 'partner_longitude', 'partner_latitude'])
        return {'status_code': 200, 'is_error': False, "message": 'location updated', 'result_rpo': ''}

    # @http.route('/sokia/upload_customer_files', type='http', auth="public", methods=['POST'], csrf=False)
    # def upload_customer_files(self, file, **kw):
    #
    #     files = request.httprequest.files.getlist('document')
    #     for file in files:
    #         if file.filename:
    #             attachment_value = {
    #                 'name': file.filename,
    #                 'datas': base64.encodebytes(file.read()),
    #                 'res_model': 'approval.request',
    #                 'res_id': approval_request.id,
    #             }
    #
    #             attachment_id = request.env['ir.attachment'].sudo().create(
    #                 attachment_value)
    #
    #     return request.redirect('/my/approval_requests')
    #
    #     admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
    #
    #     file_content = base64.encodebytes(file.read())
    #     attach = admin_client['ir.attachment'].create({
    #         'name': 'partner.png',
    #         'type': 'binary',
    #         'res_model': 'crm.lead',
    #         'mimetype': 'image/png',
    #         'datas': file_content,
    #         'res_id': 0,
    #         'res_name': 'Administrator'
    #     })
    #     # return {'result_rpo': attach.id}
    #     # return 'attach'
    #     # except Exception as e:
    #     #     return {'error': str(e)}

    @http.route('/sokia/create_customer_company', type='json', auth="public", methods=['POST'], csrf=False)
    def create_customer_company(self, **kw):
        # import tempfile
        """{
            "params":{
                "customer_name": "",
                "company_type": "",
                "street": "",
                "city": "",
                "long": "",
                "lat": "",
                "mobile": "",
                "price_list_id": "",
                "company_name": "",
                "email": "",
                "tax_id": "",
                "register_number": "",
                "salesperson_id": "",
                "documents": []
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        # if not kw.get('customer_name'):
        #     return {'status_code': 200, 'is_error': True, "message": 'Please insert customer name.', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        lead = request.env['crm.lead'].sudo().create({
            'type': 'lead',
            'name': kw.get('customer_name'),
            'company_type': kw.get('company_type'),
            'contact_name': kw.get('customer_name'),
            'long': kw.get('long'),
            'lat': kw.get('lat'),
            'street': kw.get('street'),
            'city': kw.get('city') if kw.get('city') else '',
            'mobile': kw.get('mobile'),
            'price_list_id': kw.get('price_list_id') if kw.get('price_list_id') else False,
            # 'partner_name': kw.get('company_name'),
            'tax_id': kw.get('tax_id'),
            'register_number': kw.get('register_number'),
            'email_from': kw.get('email'),
            'user_id': kw.get('salesperson_id')
        })

        if kw.get('documents'):
            for doc in kw.get('documents'):
                decoded_image = base64.b64decode(doc)
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': 'image_%s.png' % lead.id,  # Set the name of the attachment
                    'type': 'binary',
                    'datas': base64.b64encode(decoded_image),  # Set the decoded binary data as the attachment data
                    'res_model': 'crm.lead',  # Specify the model to which the attachment belongs
                    'res_id': lead.id,  # Specify the ID of the record to which the attachment is attached
                })

        return {'status_code': 200, 'is_error': False, 'message': 'Customer created successfully',
                'result_rpo': lead.id}

    @http.route('/sokia/get_visits', type='json', auth="public", methods=['POST'])
    def get_visits(self, **kw):
        """{
            "params":{
                "salesperson_id": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, "message": "Cannot get all visits, please specify salesperson to get his visits.", 'result_rpo': ''}

        salesperson_id = int(kw.get('salesperson_id'))
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        stage = admin_client['crm.stage'].search([('is_today', '=', True)])
        opportunities = admin_client['crm.lead'].search([('user_id', '=', salesperson_id), ('visit_date', '=', date.today()),
                                                         ('partner_id', '!=', False),
                                                         ('type', '=', 'opportunity'), ('stage_id', '=', stage[0])])  # checkbox of today stage
        opportunity_data = admin_client['crm.lead'].read(opportunities, ['id', 'partner_id'])
        opportunity_data_list = json.loads(json.dumps(opportunity_data))

        for opportunity in opportunity_data_list:
            invoices = admin_client['account.move'].search([('type', '=', 'out_invoice'), ('state', '=', 'posted'),
                                                            ('partner_id', '=', opportunity['partner_id'][0])])
            invoices_data = admin_client['account.move'].read(invoices, ['amount_total'])
            invoice_data_list = json.loads(json.dumps(invoices_data))

            totals = 0.00
            for total in invoice_data_list:
                totals += total['amount_total']

            opportunity['total'] = round(totals, 2)

            partner = admin_client['res.partner'].search([('id', '=', opportunity['partner_id'][0])])
            partner_data = admin_client['res.partner'].read(partner, ['property_account_receivable_id'])
            partner_data_list = json.loads(json.dumps(partner_data))

            items = admin_client['account.move.line'].search([('partner_id', '=', opportunity['partner_id'][0]),
                                                              ('parent_state', '=', 'posted'),
                                                              ('account_id', '=', partner_data_list[0]['property_account_receivable_id'][0])])
            items_data = admin_client['account.move.line'].read(items, ['debit', 'credit'])
            items_data_list = json.loads(json.dumps(items_data))

            balance = 0.00
            for line in items_data_list:
                balance += line['debit']
                balance -= line['credit']

            opportunity['balance'] = balance
            if balance == 0.0:
                opportunity['status'] = "no amount due"
            else:
                opportunity['status'] = "has amount due %s" % balance

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'visits': opportunity_data_list}

    @http.route('/sokia/get_visit_data', type='json', auth="public", methods=['POST'])
    def get_visit_data(self, **kw):
        """{
            "params":{
                "visit_id": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('visit_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add visit_id", 'result_rpo': ''}

        visit = int(kw.get('visit_id'))
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        opportunity = admin_client['crm.lead'].search([('id', '=', visit)])
        opportunity_data = admin_client['crm.lead'].read(opportunity, ['partner_id', 'user_id'])
        opportunity_data_list = json.loads(json.dumps(opportunity_data))

        partner = admin_client['res.partner'].search([('id', '=', opportunity_data_list[0]['partner_id'][0])])
        partner_data = admin_client['res.partner'].read(partner, ['street', 'partner_longitude', 'partner_latitude', 'property_product_pricelist', 'is_location_exception'])
        partner_data_list = json.loads(json.dumps(partner_data))

        opportunity_data_list[0]['street'] = partner_data_list[0]['street'] or ""
        opportunity_data_list[0]['partner_longitude'] = partner_data_list[0]['partner_longitude']
        opportunity_data_list[0]['partner_latitude'] = partner_data_list[0]['partner_latitude']
        opportunity_data_list[0]['is_location_exception'] = partner_data_list[0]['is_location_exception']
        opportunity_data_list[0]['price_list'] = partner_data_list[0]['property_product_pricelist']

        invoices = admin_client['account.move'].search([('type', '=', 'out_invoice'), ('state', '=', 'posted'),
                                                        ('partner_id', '=', opportunity_data_list[0]['partner_id'][0])])
        invoices_data = admin_client['account.move'].read(invoices, ['amount_total'])
        invoice_data_list = json.loads(json.dumps(invoices_data))

        totals = 0.00
        for total in invoice_data_list:
            totals += total['amount_total']

        opportunity_data_list[0]['total'] = round(totals, 2)

        partner = admin_client['res.partner'].search([('id', '=', opportunity_data_list[0]['partner_id'][0])])
        partner_data = admin_client['res.partner'].read(partner, ['property_account_receivable_id'])
        partner_data_list = json.loads(json.dumps(partner_data))

        items = admin_client['account.move.line'].search([('partner_id', '=', opportunity_data_list[0]['partner_id'][0]),
                                                          ('parent_state', '=', 'posted'),
                                                          ('account_id', '=',
                                                           partner_data_list[0]['property_account_receivable_id'][0])])
        items_data = admin_client['account.move.line'].read(items, ['debit', 'credit'])
        items_data_list = json.loads(json.dumps(items_data))

        balance = 0.00
        for line in items_data_list:
            balance += line['debit']
            balance -= line['credit']

        opportunity_data_list[0]['balance'] = balance
        if balance == 0.0:
            opportunity_data_list[0]['status'] = "no amount due"
        else:
            opportunity_data_list[0]['status'] = "has amount due %s" % balance

        return {'status_code': 200, 'is_error': False, "message": 'done', 'visit_data': opportunity_data_list}

    @http.route('/sokia/set_visit_date', type='json', auth="public", methods=['POST'])
    def set_visit_date(self, **kw):
        """{
            "params":{
                "visit_id": ""
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('visit_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add visit_id", 'result_rpo': ''}

        visit = int(kw.get('visit_id'))
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        opportunity = admin_client['crm.lead'].search([('id', '=', visit)])
        vals = {'visit_start': datetime.datetime.now()}
        admin_client['crm.lead'].write(opportunity[0], vals)

        return {'status_code': 200, 'is_error': False, "message": "Visit started successfully."}

    @http.route('/sokia/get_journals', type='json', auth="public", methods=['POST'])
    def get_journals(self, **kw):
        """{
            "params": {
                "salesperson_id": "",
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add salesperson_id", 'result_rpo': ''}

        journal_data_list = []
        # journals = request.env['account.journal'].sudo().search([('type', 'in', ['bank'])])
        salesperson = request.env['res.users'].sudo().search([('id', '=', int(kw.get('salesperson_id')))])
        journal_data_list.append({
            'id': salesperson.journal_id.id or "",
            'name': salesperson.journal_id.name or "",
            'type': salesperson.journal_id.type or ""
        })
        for journal in salesperson.bank_journal_ids:
            # bank_journal_id = request.env['account.journal'].sudo().search([('id', '=', journal.id)])
            journal_data_list.append({
                'id': journal.id or "",
                'name': journal.name or "",
                'type': journal.type or ""
            })

        # for journal in journals:
        #     journal_data_list.append({
        #         'id': journal.id or "",
        #         'name': journal.name or "",
        #         'type': journal.type or ""
        #     })

        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        # journals = admin_client['account.journal'].search([('type', 'in', ['cash', 'bank'])])
        # journal_data = admin_client['account.journal'].read(journals, ['id', 'name', 'type'])
        # journal_data_list = json.loads(json.dumps(journal_data))

        return {'status_code': 200, 'is_error': False, "message": "done", 'journals': journal_data_list}

    @http.route('/sokia/create_payments', type='json', auth="public", methods=['POST'])
    def create_payment(self, **kw):
        """{
            "params":{
                "salesperson_id": "",
                "customer_id": "",
                "amount": "",
                "journal_id": "",
                "date": "",
                "memo": "",
                "opportunity_id": "",
                "documents": [""]
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('customer_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add customer_id", 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add salesperson_id", 'result_rpo': ''}
        if not kw.get('journal_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add journal_id", 'result_rpo': ''}
        if not kw.get('date'):
            return {'status_code': 200, 'is_error': True, "message": "Please add date", 'result_rpo': ''}
        if not kw.get('amount'):
            return {'status_code': 200, 'is_error': True, "message": "Please add amount", 'result_rpo': ''}
        if not kw.get('opportunity_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add opportunity_id", 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        method = admin_client['account.payment.method'].search([('name', '=', 'Manual')])
        # payment = admin_client['account.payment'].create({
        payment = request.env['account.payment'].sudo().create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': int(kw.get('customer_id')),
            'journal_id': int(kw.get('journal_id')),
            'payment_method_id': method[0],
            'amount': float(kw.get('amount')),
            'payment_date': kw.get('date'),
            'communication': kw.get('memo'),
            'salesperson_id': int(kw.get('salesperson_id'))
        })

        if kw.get('documents'):
            for doc in kw.get('documents'):
                decoded_image = base64.b64decode(doc)
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': 'image_pay_%s.png' % payment.id,  # Set the name of the attachment
                    'type': 'binary',
                    'datas': base64.b64encode(decoded_image),  # Set the decoded binary data as the attachment data
                    'res_model': 'account.payment',  # Specify the model to which the attachment belongs
                    'res_id': payment.id,  # Specify the ID of the record to which the attachment is attached
                })

        payment.sudo().post()
        # pdf = request.env.ref('account.action_report_payment_receipt').sudo().render_qweb_pdf([payment.id])[0]
        # pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        # payment_printout = '%s/report/pdf/account.report_payment_receipt/%s' % (self.url_domain, payment.id)
        settings = http.request.env['res.config.settings'].sudo().get_values()
        url_domain = settings['p_domain']
        payment_printout = '%s/sokia/print_id/%s' % (url_domain, payment.id)
        stage = admin_client['crm.stage'].search([('is_visited', '=', True)])
        opportunity = admin_client['crm.lead'].search([('id', '=', int(kw.get('opportunity_id')))])
        vals = {'visit_end': datetime.datetime.now(), 'stage_id': stage[0]}
        admin_client['crm.lead'].write(opportunity[0], vals)

        return {'status_code': 200, 'is_error': False, 'message': 'Payment created successfully.',
                'result_rpo': [payment.id, payment_printout]}

    @http.route('/sokia/print_id/<int:payment_id>', methods=['POST', 'GET'], csrf=False, type='http', auth="public", website=True)
    def print_id(self, payment_id=False):
        # student_id = kw['stud_id']
        # if student_id:
        pdf = request.env.ref('account.action_report_payment_receipt').sudo().render_qweb_pdf([payment_id])[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route('/sokia/print_invoice_id/<int:invoice_id>', methods=['POST', 'GET'], csrf=False, type='http', auth="public",
                website=True)
    def print_invoice_id(self, invoice_id=False):
        # student_id = kw['stud_id']
        # if student_id:
        pdf = request.env.ref('account.account_invoices').sudo().render_qweb_pdf([invoice_id])[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route('/sokia/create_sales_order', type='json', auth="public", methods=['POST'])
    def create_so(self, **kw):
        """{
            "params":{
                "customer_id": "",
                "pricelist_id": "",
                "salesperson_id": "",
                "warehouse_id": "",
                "picking_policy": "direct",
                "opportunity_id": "",
                "items": [
                    {
                        "product_id": "",
                        "quantity": "",
                        "price": ""
                    }
                ]
            }
        }"""

        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('customer_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add customer_id", 'result_rpo': ''}
        if not kw.get('pricelist_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add pricelist_id", 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add salesperson_id", 'result_rpo': ''}
        if not kw.get('opportunity_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add opportunity_id", 'result_rpo': ''}
        if not kw.get('items'):
            return {'status_code': 200, 'is_error': True, "message": "Please add items", 'result_rpo': ''}
        for item in kw.get('items'):
            if not item['product_id']:
                return {'status_code': 200, 'is_error': True, "message": "Please add product_id", 'result_rpo': ''}
            if not item['quantity']:
                return {'status_code': 200, 'is_error': True, "message": "Please add quantity", 'result_rpo': ''}
            if not item['price']:
                return {'status_code': 200, 'is_error': True, "message": "Please add price", 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        # opportunity = admin_client['crm.lead'].search([('id', '=', int(kw.get('opportunity_id')))])
        user = admin_client['res.users'].search([('id', '=', int(kw.get('salesperson_id')))])
        user_data = admin_client['res.users'].read(user, ['id', 'warehouse_id'])
        user_data_list = json.loads(json.dumps(user_data))

        customer = request.env['res.partner'].sudo().search([('id', '=', int(kw.get('customer_id')))])
        customer_balance = customer.credit - customer.debit
        total_order = 0.00
        for item in kw.get('items'):
            salesperson = request.env['res.users'].sudo().search([('id', '=', int(kw.get('salesperson_id')))])
            location = request.env['stock.location'].sudo().search([('id', '=', salesperson.location_id.id)])
            onhand_items = request.env['stock.quant'].sudo().search([('product_id', '=', int(item['product_id'])),
                                                                     ('location_id', '=', location.id)])
            stock_qty = sum(onhand_items.mapped('quantity'))
            if int(item['quantity']) > stock_qty:
                product = request.env['product.product'].sudo().search([('id', '=', int(item['product_id']))])
                return {'status_code': 200, 'is_error': True,
                        'message': 'The quantity order of %s greater than quantity on hand'
                                   % product.name, 'result_rpo': ''}

            total_order += float(item['price'])

        if customer.credit_check and (customer_balance + total_order) > customer.credit_blocking:
            return {'status_code': 200, 'is_error': True,
                    'message': 'This customer exceeded the credit limit %s, with customer credit balance of %s and sales order total amount of %s'
                               % (customer.credit_blocking, customer_balance, total_order), 'result_rpo': ''}

        sale_order = admin_client['sale.order'].create({
            "partner_id": int(kw.get('customer_id')),
            "date_order": datetime.datetime.now(),
            "pricelist_id": int(kw.get('pricelist_id')),
            "user_id": int(kw.get('salesperson_id')),
            "warehouse_id": user_data_list[0]['warehouse_id'][0],
            # "warehouse_id": int(kw.get('warehouse_id')),
            "picking_policy": "direct",
            "opportunity_id": int(kw.get('opportunity_id')),
            "is_from_app": True
            # "item": kw.get('items')
        })
        for item in kw.get('items'):
            product = admin_client['product.product'].search([('product_tmpl_id', '=', int(item['product_id']))])
            product_data = admin_client['product.product'].read(product, ['id', 'name', 'uom_id'])
            product_data_list = json.loads(json.dumps(product_data))
            # return {'status': 'success', 'product': product_data_list}

            item_unit_price = float(item['price'])
            if kw.get('pricelist_id'):
                product = request.env['product.product'].sudo().search([('id', '=', int(product_data_list[0]['id']))])
                price_list_item = request.env['product.pricelist.item'].sudo().search([('pricelist_id', '=', int(kw.get('pricelist_id')))])
                for line in price_list_item:
                    if line.applied_on == '0_product_variant':
                        if line.product_id.id == product.id and float(item['quantity']) >= line.min_quantity:
                            item_unit_price = line.fixed_price
                            break
                    elif line.applied_on == '1_product':
                        if line.product_tmpl_id.id == product.product_tmpl_id.id and float(item['quantity']) >= line.min_quantity:
                            item_unit_price = line.fixed_price
                            break
                    elif line.applied_on == '2_product_category':
                        if line.categ_id.id == product.categ_id.id and float(item['quantity']) >= line.min_quantity:
                            item_unit_price = line.fixed_price
                            break
                    else:
                        if float(item['quantity']) >= line.min_quantity:
                            item_unit_price = line.fixed_price
                            break

                order_lines = admin_client['sale.order.line'].create({
                    "product_id": int(product_data_list[0]['id']),
                    "name": product_data_list[0]['name'],
                    "product_uom_qty": float(item['quantity']),
                    "price_unit": item_unit_price,
                    "order_id": sale_order
                })
        stage = admin_client['crm.stage'].search([('is_visited', '=', True)])
        opportunity = admin_client['crm.lead'].search([('id', '=', int(kw.get('opportunity_id')))])
        vals = {'visit_end': datetime.datetime.now(), 'stage_id': stage[0]}
        admin_client['crm.lead'].write(opportunity[0], vals)
        request.cr.commit()
        # Buy X get Y
        order = request.env['sale.order'].sudo().browse(sale_order)
        order.recompute_coupon_lines()
        try:
            order.confirm_so_cycle()
        except:
            return {'status_code': 400, 'is_error': True, 'message': 'I cannot validate delivery order',
                    'result_rpo': ''}

        invoice = order.invoice_ids[0]

        settings = http.request.env['res.config.settings'].sudo().get_values()
        url_domain = settings['p_domain']
        invoice_printout = '%s/sokia/print_invoice_id/%s' % (url_domain, invoice.id)

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': [sale_order, invoice_printout]}

    @http.route('/sokia/create_credit_note', type='json', auth="public", methods=['POST'])
    def create_credit_note(self, **kw):
        """{
            "params": {
                "invoice_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('invoice_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add invoice_id", 'result_rpo': ''}
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        invoice = request.env['account.move'].sudo().search([('id', '=', int(kw.get('invoice_id')))])
        # invoice = admin_client['account.move'].search([('id', '=', int(kw.get('invoice_id')))])
        credit_note = invoice._reverse_moves()
        credit_note.action_post()

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': credit_note,}

    @http.route('/sokia/create_credit_note_details', type='json', auth="public", methods=['POST'])
    def create_credit_note_details(self, **kw):
        """{
            "params": {
                "invoice_id": "",
                "items": [{
                    "product_id": "",
                    "description": "",
                    "quantity": "",
                    "unit_price": ""
                }]
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('invoice_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add invoice_id", 'result_rpo': ''}
        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        invoice = request.env['account.move'].sudo().search([('id', '=', int(kw.get('invoice_id')))])
        items = []
        for item in kw.get('items'):
            product = request.env['product.product'].sudo().search([('id', '=', int(item['product_id']))])
            items.append((0, 0, {
                'product_id': int(item['product_id']),
                'name': item['description'],
                'account_id': product.property_account_income_id.id,
                'quantity': float(item['quantity']),
                'price_unit': float(item['unit_price']),
                'tax_ids': product.taxes_id.ids,
                # 'move_id': credit_note
            }))

        credit_note = admin_client['account.move'].create({
            'partner_id': invoice.partner_id.id,
            'type': 'out_refund',
            'ref': 'Reversal of: %s' % invoice.name,
            'invoice_user_id': invoice.invoice_user_id.id,
            'team_id': invoice.team_id.id,
            'invoice_line_ids': items
        })

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': credit_note}

    @http.route('/sokia/get_all_products', type='json', auth="public", methods=['POST'])
    def get_all_products(self, **kw):
        """{
            "params": {
                "salesperson_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add salesperson_id", 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        products = admin_client['product.template'].search([])
        products_data = admin_client['product.template'].read(products, ['id', 'name', 'description_sale',
                                                                         'list_price', 'taxes_id', 'uom_id'])
        products_data_list = json.loads(json.dumps(products_data))
        for item in products_data_list:
            if not item['description_sale']:
                item['description_sale'] = ""
            if not item['taxes_id']:
                item['taxes_id'] = []
            item['image'] = self.product_tmpl_data(item['id'])

        return {'status_code': 200, 'is_error': False, "message": "Products Data", 'result_rpo': products_data_list}

    @http.route('/sokia/get_reasons', type='json', auth="public", methods=['POST'], csrf=False)
    def get_reasons(self, **kw):
        """{
            "params": {
                "salesperson_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add salesperson_id", 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        reason = admin_client['crm.lost.reason'].search([])
        reason_data = admin_client['crm.lost.reason'].read(reason, ['id', 'name'])
        reason_data_list = json.loads(json.dumps(reason_data))

        return {'status_code': 200, 'is_error': False, "message": "done", 'result_rpo': reason_data_list}

    @http.route('/sokia/lost_reason', type='json', auth="public", methods=['POST'])
    def lost_reason(self, **kw):
        """{
            "params": {
                "opportunity_id": "",
                "reason_id": "",
                "lost_reason_details": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('opportunity_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add opportunity_id", 'result_rpo': ''}
        if not kw.get('reason_id'):
            return {'status_code': 200, 'is_error': True, "message": "Please add reason_id", 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        stage = admin_client['crm.stage'].search([('is_lost', '=', True)])
        opportunity = admin_client['crm.lead'].search([('id', '=', int(kw.get('opportunity_id')))])
        vals = {'lost_reason': int(kw.get('reason_id')), 'lost_reason_details': kw.get('lost_reason_details'),
                'visit_end': datetime.datetime.now(), 'stage_id': stage[0]}
        admin_client['crm.lead'].write(opportunity[0], vals)

        return {'status_code': 200, 'is_error': False, "message": "Don\'t deal successfully."}

    @http.route('/sokia/get_invoices_credits', type='json', auth="public", methods=['POST'])
    def get_invoices_credits(self, **kw):
        """{
            "params": {
                "customer_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('customer_id'):
            return {'status_code': 400, 'is_error': True, "message": "Please add customer_id", 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        partner_invoice = admin_client['account.move'].search([('partner_id', '=', int(kw.get('customer_id'))),
                                                               ('type', 'in', ['out_invoice', 'out_refund']),
                                                               ('state', '=', 'posted')])
        partner_invoice_data = admin_client['account.move'].read(partner_invoice, ['name', 'type', 'invoice_date', 'partner_id',
                                                                                   'invoice_line_ids', 'amount_total'])
        partner_invoice_data_list = json.loads(json.dumps(partner_invoice_data))
        for invoice in partner_invoice_data_list:
            if invoice['type'] == 'out_invoice':
                invoice['type'] = 'Invoice'
            else:
                invoice['type'] = 'Credit Note'

            invoice['num_products'] = len(invoice['invoice_line_ids'])

        return {'status_code': 200, 'is_error': False, "message": "Invoices of partner.", 'result_rpo': partner_invoice_data_list}

    @http.route('/sokia/get_details_invoices_credits', type='json', auth="public", methods=['POST'])
    def get_details_invoices_credits(self, **kw):
        """{
            "params": {
                "invoice_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('invoice_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please add invoice_id', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        invoice = admin_client['account.move'].search([('id', '=', int(kw.get('invoice_id')))])
        invoice_data = admin_client['account.move'].read(invoice, ['invoice_line_ids', 'amount_tax', 'amount_total'])
        invoice_data_list = json.loads(json.dumps(invoice_data))

        lines = []
        for line in invoice_data_list[0]['invoice_line_ids']:
            invoice_line = admin_client['account.move.line'].search([('id', '=', line)])
            invoice_line_data = admin_client['account.move.line'].read(invoice_line, ['product_id', 'name', 'quantity',
                                                                                      'price_unit', 'tax_ids',
                                                                                      'price_subtotal'])
            invoice_line_data_list = json.loads(json.dumps(invoice_line_data))
            invoice_line_data_list[0]['image'] = self.product_data(invoice_line_data_list[0]['product_id'][0])
            lines.append(invoice_line_data_list[0])

        invoice_data_list[0]['items'] = lines

        return {'status_code': 200, 'is_error': False, "message": "Items of invoice.", 'result_rpo': invoice_data_list}

    @http.route('/sokia/post_visit', type='json', auth="public", methods=['POST'])
    def post_visit(self, **kw):
        """{
            "params":{
                "customer_id": "",
                "salesperson_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('customer_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert customer_id.', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert salesperson_id.', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        customer = request.env['res.partner'].sudo().search([('id', '=', int(kw.get('customer_id')))])
        stage = request.env['crm.stage'].sudo().search([('is_today', '=', True)])
        today_date = fields.Datetime.today()
        opportunity = admin_client['crm.lead'].create({
            'type': "opportunity",
            'partner_id': int(kw.get('customer_id')),
            'stage_id': stage.id,
            'name': customer.name,
            'company_type': customer.company_type,
            'visit_date': today_date,
            # 'contact_name': kw.get('customer_name'),
            # 'long': kw.get('long'),
            # 'lat': kw.get('lat'),
            'street': customer.street,
            'city': customer.city,
            'mobile': customer.mobile,
            # 'price_list_id': customer.proprty_product_pricelist.id,
            # 'partner_name': kw.get('company_name'),
            'tax_id': customer.vat,
            'register_number': customer.registry_num,
            'email_from': customer.email,
            'user_id': kw.get('salesperson_id')
        })

        return {"status_code": 200, 'is_error': False, 'message': 'done', "result": opportunity}

    @http.route('/sokia/get_month_statistics', type='json', auth="public", methods=['POST'])
    def get_month_statistics(self, **kw):
        """{
            "params":{
                "salesperson_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert salesperson_id.', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)

        today = fields.Date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(
            days=1)

        customers = request.env['res.partner'].sudo().search([('user_id', '=', int(kw.get('salesperson_id'))),
                                                              ('create_date', '>=', first_day_of_month),
                                                              ('create_date', '<=', last_day_of_month)])
        customer_num = len(customers)

        invoices = request.env['account.move'].sudo().search([('invoice_user_id', '=', int(kw.get('salesperson_id'))),
                                                              ('invoice_date', '>=', first_day_of_month),
                                                              ('invoice_date', '<=', last_day_of_month),
                                                              ('state', '=', 'posted')])

        total_invoices = sum(invoices.mapped('amount_total'))

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': [{'customers_num': customer_num,
                                                                                      'total_invoices': total_invoices}]}

    @http.route('/sokia/get_daily_statistics', type='json', auth="public", methods=['POST'])
    def get_daily_statistics(self, **kw):
        """{
            "params":{
                "salesperson_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert salesperson_id.', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)

        today = fields.Date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(
            days=1)

        user = request.env['res.users'].sudo().search([('id', '=', int(kw.get('salesperson_id')))])
        stage = request.env['crm.stage'].sudo().search([('is_today', '=', True)])
        opportunity = request.env['crm.lead'].sudo().search([('user_id', '=', int(kw.get('salesperson_id'))),
                                                             ('stage_id', '=', stage.id)])
        opportunity_num = len(opportunity)

        # payments = request.env['account.payment'].sudo().search([('salesperson_id', '=', int(kw.get('salesperson_id'))),
        #                                                          ('payment_date', '>=', first_day_of_month),
        #                                                          ('payment_date', '<=', last_day_of_month)])
        # total_payments = sum(payments.mapped('amount'))

        journal_items = request.env['account.move.line'].sudo().search(
            [('account_id', '=', user.journal_id.default_debit_account_id.id),
             ('move_id.state', '=', 'posted')])
        balance = sum(journal_items.mapped('debit')) - sum(journal_items.mapped('credit'))

        location = request.env['stock.location'].sudo().search([('id', '=', user.location_id.id)])
        onhand_items = request.env['stock.quant'].sudo().search([('location_id', '=', location.id)])

        items_num = sum(onhand_items.mapped('quantity'))

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': [{'visits_num': opportunity_num,
                                                                                          'income': balance,
                                                                                          'items_num': items_num}]}

    @http.route('/sokia/get_stock_statistics', type='json', auth="public", methods=['POST'])
    def get_stock_statistics(self, **kw):
        """{
            "params":{
                "salesperson_id": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert salesperson_id.', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        user = request.env['res.users'].sudo().search([('id', '=', int(kw.get('salesperson_id')))])
        location = request.env['stock.location'].sudo().search([('id', '=', user.location_id.id)])
        onhand_items = request.env['stock.quant'].sudo().search([('location_id', '=', location.id)])

        items_list = []
        for item in onhand_items:
            # product = request.env['product.product'].sudo().search([('id', '=', item.product_id)])
            items_list.append({
                'item': item.product_id.id,
                'item_name': item.product_id.name,
                'quantity': item.quantity
            })

        return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': items_list}

    @http.route('/sokia/stock_transfers', type='json', auth="public", methods=['POST'])
    def stock_transfers(self, **kw):
        """{
            "params":{
                "salesperson_id": "",
                "items": [{
                    "product_id": "",
                    "quantity": ""
                }]
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert salesperson_id.', 'result_rpo': ''}
        if not kw.get('items'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert product_id.', 'result_rpo': ''}
        # if not kw.get('quantity') or float(kw.get('quantity')) < 1.00:
        #     return {'status_code': 200, 'is_error': True, 'message': 'Please insert quantity.', 'result_rpo': ''}

        salesperson = request.env['res.users'].sudo().search([('id', '=', int(kw.get('salesperson_id')))])

        picking_type_id = request.env['stock.picking.type'].sudo().search([('code', '=', 'internal'),
                                                                           ('default_location_src_id', '=',
                                                                            salesperson.wh_location_id.id)])

        if not picking_type_id:
            return {'status_code': 200, 'is_error': True,
                    'message': 'Please set a valid warehouse location on salesperson.', 'result_rpo': ''}

        moves = []
        for item in kw.get('items'):
            product = request.env['product.product'].sudo().search([('id', '=', int(item['product_id']))])
            moves.append((0, 0, {
                'product_id': product.id,
                'name': product.name,
                'product_uom_qty': float(item['quantity']),
                'product_uom': product.uom_id.id
            }))

        transfer = request.env['stock.picking'].sudo().create({
            'state': 'draft',
            'scheduled_date': datetime.datetime.now(),
            'picking_type_id': picking_type_id.id,
            'location_id': salesperson.wh_location_id.id,
            'location_dest_id': salesperson.location_id.id,
            'salesperson_id': salesperson.id,
            'move_ids_without_package': moves
        })

        return {'status_code': 200, 'is_error': False, 'message': 'stock request done', 'result_rpo': transfer.id}

    @http.route('/sokia/get_search_customers', type='json', auth="public", methods=['POST'])
    def get_search_customers(self, **kw):
        """{
            "params":{
                "salesperson_id": "",
                "search_with": ""
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('salesperson_id'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert salesperson_id.', 'result_rpo': ''}
        # if not kw.get('search_with'):
        #     return {'status_code': 200, 'is_error': True, 'message': 'No test to search.', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        partners = request.env['res.partner'].sudo().search([('user_id', '=', int(kw.get('salesperson_id')))])

        customers_searched_list = []
        customers_all_list = []
        for partner in partners:
            # if kw.get('search_with') and kw.get('search_with') in partner.name:
            invoices = request.env['account.move'].sudo().search([('type', '=', 'out_invoice'), ('state', '=', 'posted'),
                                                                  ('partner_id', '=', partner.id)])

            items = request.env['account.move.line'].sudo().search([('partner_id', '=', partner.id), ('parent_state', '=', 'posted'),
                                                                    ('account_id', '=', partner.property_account_receivable_id.id)])
            balance = 0.0
            for item in items:
                balance += item.debit
                balance -= item.credit

            customers_all_list.append({
                'id': partner.id,
                'name': partner.name,
                'street': partner.street or "",
                'company_type': partner.company_type or "",
                'total': sum(invoices.mapped('amount_untaxed')),
                'balance': balance
            })

        for partner in partners:
            if kw.get('search_with') and kw.get('search_with') in partner.name:
                invoices = request.env['account.move'].sudo().search([('type', '=', 'out_invoice'), ('state', '=', 'posted'),
                                                                      ('partner_id', '=', partner.id)])

                items = request.env['account.move.line'].sudo().search([('partner_id', '=', partner.id), ('parent_state', '=', 'posted'),
                                                                        ('account_id', '=', partner.property_account_receivable_id.id)])
                balance = 0.0
                for item in items:
                    balance += item.debit
                    balance -= item.credit

                customers_searched_list.append({
                    'id': partner.id,
                    'name': partner.name,
                    'street': partner.street or "",
                    'company_type': partner.company_type or "",
                    'total': sum(invoices.mapped('amount_untaxed')),
                    'balance': balance
                })

        if customers_searched_list:
            return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': customers_searched_list}
            # return {'status_code': 200, 'is_error': False, 'message': 'No data with this search.', 'result_rpo': customers_searched_list}
        elif not customers_searched_list and kw.get('search_with'):
            return {'status_code': 200, 'is_error': False, 'message': 'No data with this search.',
                    'result_rpo': customers_searched_list}
        elif customers_all_list:
            return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': customers_all_list}
        else:
            return {'status_code': 200, 'is_error': False, 'message': 'No result for this salesperson.',
                    'result_rpo': []}

    @http.route('/sokia/get_items_price_before_order', type='json', auth="public", methods=['POST'])
    def get_items_price_before_order(self, **kw):
        """{
            "params":{
                "items": [{
                    "product_id": "1",
                    "quantity": "5",
                    "price_list": "1"
                }]
            }
        }"""
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}
        if not kw.get('items'):
            return {'status_code': 200, 'is_error': True, 'message': 'Please insert list of items.', 'result_rpo': ''}

        admin_client = Client(self.set_test_app_domains()['ip'], self.set_test_app_domains()['db'], self.set_test_app_domains()['admin_login'], self.set_test_app_domains()['admin_pass'])
        # admin_client = Client(self.url, self.database, self.admin_login, self.admin_pass)
        result = []
        items_list = []
        total = 0.00
        for item in kw.get('items'):
            product = request.env['product.product'].sudo().search([('id', '=', int(item['product_id']))])
            price_list = request.env['product.pricelist'].sudo().search([('id', '=', int(item['price_list']))])
            item_unit_price = product.list_price
            price_list_item = request.env['product.pricelist.item'].sudo().search(
                [('pricelist_id', '=', int(item['price_list']))])
            for line in price_list_item:
                if line.applied_on == '0_product_variant':
                    if line.product_id.id == product.id and float(item['quantity']) >= line.min_quantity:
                        item_unit_price = line.fixed_price
                        break
                elif line.applied_on == '1_product':
                    if line.product_tmpl_id.id == product.product_tmpl_id.id and float(item['quantity']) >= line.min_quantity:
                        item_unit_price = line.fixed_price
                        break
                elif line.applied_on == '2_product_category':
                    if line.categ_id.id == product.categ_id.id and float(item['quantity']) >= line.min_quantity:
                        item_unit_price = line.fixed_price
                        break
                else:
                    if float(item['quantity']) >= line.min_quantity:
                        item_unit_price = line.fixed_price
                        break

            items_list.append({
                'product_id': product.id,
                'product_name': product.name,
                'quantity': float(item['quantity']),
                'unit_price': item_unit_price
            })

        for line in items_list:
            total += (line['unit_price'] * line['quantity'])

            # Buy X get Y
            pricelist_obj = request.env['product.pricelist'].sudo()
            promo_qty = pricelist_obj.get_pricelist_qty(line['quantity'], line['product_id'])
            if promo_qty:
                line['quantity'] += promo_qty

        result.append({
            "items": items_list,
            "total": total
        })

        if result:
            return {'status_code': 200, 'is_error': False, 'message': 'done', 'result_rpo': result}







