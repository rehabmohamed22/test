import logging
import json
import re
from odoo import SUPERUSER_ID
from odoo.exceptions import AccessDenied
import jwt
import datetime
from urllib.parse import parse_qs
from odoo.http import request
from odoo import http, fields
import traceback
from odoo import Command


_logger = logging.getLogger(__name__)
SECRET_KEY = "MY_SECRET_KEY"

def valid_response(data,status,pagination_info=None):
    response_body={
        'data':data,
        'message':"successfil",
    }
    if pagination_info:
        response_body['pagination_info']=pagination_info
    return request.make_json_response(response_body,status=status)



class productApi(http.Controller):


    def get_allowed_fields(self, fetch_id):

        return [rec.name for rec in fetch_id.fields_api]


    ####################### collection ###########################ok
    @http.route("/v1/collection/data", methods=["GET"], type="http", auth="none", csrf=False)
    def get_collection_data(self):
        # ✅ 1. استخراج الـ Token من الـ Header والتحقق منه
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_json_response({
                "success": False,
                "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"
            }, status=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = request.env['res.users'].sudo().browse(user_id)

            if not user:
                return request.make_json_response({
                    "success": False,
                    "message": "المستخدم غير موجود"
                }, status=401)

        except jwt.ExpiredSignatureError:
            return request.make_json_response({
                "success": False,
                "message": "انتهت صلاحية Token"
            }, status=401)
        except jwt.InvalidTokenError:
            return request.make_json_response({
                "success": False,
                "message": "Token غير صالح"
            }, status=401)


        params = parse_qs(request.httprequest.query_string.decode('utf-8)'))
        product_domain = []
        page = offset = None
        limit = 5
        model=params.get('model')

        model = model[0] if model else ''
        if model:  # تحقق مما إذا كانت القيمة ليست فارغة
            fetch_id = request.env['fetch.data'].sudo().search([('model_name', '=', model)])
        else:
            fetch_id = request.env['fetch.data']  # إرجاع كائن فارغ بدلًا من تنفيذ بحث غير صحيح

        fields = self.get_allowed_fields(fetch_id)

        if params:
            if params.get('limit'):
                limit = int(params.get('limit')[0])
            if params.get('page'):
                page = int(params.get('page')[0])
        if page:
            offset = (page * limit) - limit


        if not fetch_id :
            return request.make_json_response("model not allowed", status=400)


        data = request.env[model].sudo().search_read(fields=fields, offset=offset, limit=limit,
                                                                order='id desc'  )
        print(model)

        if not data:
            return request.make_json_response({
                "error": "There are not records!",
            }, status=400)
        return valid_response(
            data
                               , pagination_info={
            'page': page if page else 1,
            'limit': limit,

        }, status=200)


    #########################  Register ######################
    @http.route('/api/register', type='json', auth='public', methods=['POST'], csrf=False)
    def register(self, **kwargs):
        """ تسجيل مستخدم جديد وإرجاع Token """
        data = request.httprequest.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        # التحقق من إدخال البريد الإلكتروني وكلمة المرور
        if not email or not password:
            return {"success": False, "message": "البريد الإلكتروني وكلمة المرور مطلوبان"}

        # التحقق من صحة تنسيق البريد الإلكتروني
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return {"success": False, "message": "يرجى إدخال بريد إلكتروني صحيح"}

        # التحقق من وجود المستخدم مسبقًا
        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return {"success": False, "message": "البريد الإلكتروني مستخدم بالفعل"}

        # إنشاء المستخدم الجديد
        user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'password': password,
        })

        return {
            "success": True,
            "message": "تم تسجيل المستخدم بنجاح",
            "user_id": user.id,
        }


    #########################  Login ######################
    @http.route('/api/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        """ تسجيل الدخول باستخدام JSON Web Token (JWT) """
        try:
            data = request.httprequest.get_json()
            email = data.get('email')
            password = data.get('password')

            # ✅ التحقق من صحة البيانات المدخلة
            if not email or not password:
                return {"success": False, "message": "جميع الحقول مطلوبة"}

            # ✅ البحث عن المستخدم بالبريد الإلكتروني
            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)

            if not user:
                return {"success": False, "message": "المستخدم غير موجود"}

            # ✅ استخدام الطريقة الصحيحة للمصادقة في Odoo 17
            try:
                uid = request.session.authenticate(request.db, email, password)
            except AccessDenied:
                return {"success": False, "message": "كلمة المرور غير صحيحة"}

            # ✅ إنشاء `JWT Token`
            payload = {
                "user_id": user.id,
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)  # صلاحية ليوم واحد
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return {
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "user_id": user.id,
                "token": token
            }

        except Exception as e:
            _logger.error(f"Login error: {str(e)}")
            return {"success": False, "message": f"خطأ داخلي في السيرفر: {str(e)}"}

    ######################################################## Check Token ##################################
    def authenticate_request():
        """ التحقق من صحة JWT Token """
        auth_header = request.httprequest.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return {"success": False, "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"}

        token = auth_header.split(" ")[1]  # استخراج الـ Token بعد كلمة "Bearer"

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            # التحقق مما إذا كان المستخدم موجودًا
            user = request.env["res.users"].sudo().browse(user_id)
            if not user.exists():
                return {"success": False, "message": "المستخدم غير موجود"}

            # ✅ إرجاع المستخدم إذا كان التحقق ناجحًا
            return {"success": True, "user": user}

        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "انتهت صلاحية Token"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Token غير صالح"}




    ####################### Create Journal Entry ###########################ok
    @http.route("/api/account_move/create", methods=["POST"], type="json", auth="none", csrf=False)
    def create_journal_api(self,**kwargs):
        # ✅ 1. استخراج الـ Token من الـ Header والتحقق منه
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_json_response({
                "success": False,
                "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"
            }, status=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = request.env['res.users'].sudo().browse(user_id)

            if not user.exists():
                return request.make_json_response({
                    "success": False,
                    "message": "المستخدم غير موجود"
                }, status=401)

        except jwt.ExpiredSignatureError:
            return request.make_json_response({
                "success": False,
                "message": "انتهت صلاحية Token"
            }, status=401)
        except jwt.InvalidTokenError:
            return request.make_json_response({
                "success": False,
                "message": "Token غير صالح"
            }, status=401)

        print("inside create journal")

        try:
            # 🔎 قراءة البيانات من الطلب
            args = request.httprequest.data.decode()
            vals = json.loads(args)

            # ✅ التحقق من وجود الحقول الأساسية بدون `journal_id`
            required_fields = ['move_type', 'date', 'line_ids']  # 🚀 إزالة journal_id لأنه سيُحسب تلقائيًا
            for field in required_fields:
                if field not in vals or not vals[field]:
                    return request.make_json_response({
                        'success': False,
                        'message': f'حقل مطلوب مفقود: {field}',
                        'data_received': vals  # 🔥 إرجاع البيانات المرسلة للتحقق
                    }, status=400)

            # ✅ إضافة `company_id` تلقائيًا من المستخدم
            company_id = user.company_id.id
            if not company_id:
                return request.make_json_response({
                    "success": False,
                    "message": "لم يتم العثور على شركة لهذا المستخدم"
                }, status=400)

            # ✅ البحث عن `journal_id` تلقائيًا
            journal = request.env['account.journal'].sudo().search([
                ('type', '=', 'general'),
                ('company_id', '=', company_id)  # 🔥 تأكد أن الدفتر تابع لنفس الشركة
            ], limit=1)

            if not journal:
                return request.make_json_response({
                    "success": False,
                    "message": "لم يتم العثور على دفتر محاسبي عام مناسب"
                }, status=400)

            journal_id = journal.id  # ✅ استخدام `journal_id` الذي تم العثور عليه

            # ✅ التحقق من `line_ids`
            formatted_lines = []
            for line in vals['line_ids']:
                if 'account_id' not in line[2] or 'debit' not in line[2] or 'credit' not in line[2]:
                    return request.make_json_response({
                        "success": False,
                        "message": "كل سطر في `line_ids` يجب أن يحتوي على `account_id` و `debit` و `credit`",
                        "invalid_line": line  # 🔥 إرجاع السطر الذي سبب الخطأ
                    }, status=400)

                account_id = line[2]['account_id']

                # ✅ التحقق من صحة `account_id`
                account = request.env['account.account'].sudo().browse(account_id)
                if not account.exists():
                    return [{
                        "success": False,
                        "message": f"الحساب المحاسبي غير موجود أو غير صالح: {account_id}",
                        "invalid_account_id": account_id,
                        "status": 400,
                    }]

                # ✅ إضافة القيم إلى `formatted_lines`
                formatted_lines.append((0, 0, {
                    'account_id': account_id,
                    'debit': line[2].get('debit', 0.0),
                    'credit': line[2].get('credit', 0.0),
                    'name': line[2].get('name', '/'),
                    'currency_id': line[2].get('currency_id', False)
                }))

            # 🔄 إعداد القيم
            move_vals = {
                'move_type': vals['move_type'],
                'ref': vals.get('ref', ''),
                'date': vals['date'],
                'journal_id': journal_id,  # ✅ استخدام `journal_id` المحسوب تلقائيًا
                'line_ids': formatted_lines,
                'company_id': company_id  # ✅ الشركة المرتبطة بالمستخدم
            }

            print("✅ قبل إنشاء القيد")

            # 🧾 إنشاء قيد اليومية
            try:
                journal_entry = request.env['account.move'].sudo().create(move_vals)
                print(f"✅ قيد اليومية {journal_entry.id} تم إنشاؤه بنجاح")

                try:
                    journal_entry.action_post()  # 🔥 نشر القيد تلقائيًا
                    print("✅ القيد نُشر بنجاح")
                except Exception as e:
                    print(f"❌ خطأ أثناء نشر القيد: {str(e)}")  # 🔥 طباعة الخطأ في السيرفر
                    return request.make_json_response({
                        'success': False,
                        'message': f"خطأ أثناء نشر القيد: {str(e)}"
                    }, status=500)
                print("✅ سيتم إرجاع الاستجابة الآن...")
                return [{
                    'success': True,
                    'message': 'تم إنشاء قيد اليومية بنجاح',
                    'journal_entry_id': journal_entry.id,
                    'status':201,
                }]

            except Exception as e:
                request.env.cr.rollback()  # ⛔ إلغاء المعاملة إذا فشلت
                print(f"❌ خطأ أثناء إنشاء القيد: {str(e)}")  # 🔥 طباعة الخطأ في السيرفر
                return request.make_json_response({
                    'success': False,
                    'message': f"خطأ أثناء إنشاء القيد: {str(e)}"
                }, status=500)

        except Exception as e:
            request.env.cr.rollback()  # ⛔ إلغاء المعاملة إذا فشلت
            print(f"❌ خطأ داخلي: {str(e)}")  # 🔥 طباعة الخطأ في السيرفر
            return request.make_json_response({
                'success': False,
                'message': f"خطأ داخلي: {str(e)}"
            }, status=500)



    ###################### Create Sale Order2 ###########################ok

    @http.route('/salesperson/create_order', methods=["POST"], type="json", auth="none", csrf=False)
    def create_sale_order(self):
        # 🔹 التحقق من وجود Authorization Header
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {"success": False, "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"}, 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if not user_id:
                return {"success": False, "message": "المستخدم غير موجود في الـ Token"}, 401

            # 🔹 الحل النهائي لمشكلة Expected singleton
            user = request.env['res.users'].sudo().search([('id', '=', user_id)], limit=1)

            if not user:
                return {"success": False, "message": "المستخدم غير موجود أو هناك خطأ في البيانات"}, 401

        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "انتهت صلاحية Token"}, 401
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Token غير صالح"}, 401
        except Exception as e:
            return {"success": False, "message": f"خطأ في التحقق من المستخدم: {str(e)}"}, 500

        # 🔹 التحقق من صحة البيانات
        try:
            data = json.loads(request.httprequest.data)
        except json.JSONDecodeError:
            return {"success": False, "message": "البيانات المرسلة غير صحيحة"}, 400

        required_fields = ['partner_id', 'pricelist_id', 'date_order', 'sale_order_lines']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return {"success": False, "message": f"الحقول التالية مفقودة: {', '.join(missing_fields)}"}, 400

        # 🔹 تجهيز سطور الطلب
        order_lines = []
        for line in data.get('sale_order_lines', []):
            if not line.get('product_id') or not line.get('product_uom_qty'):
                return {"success": False, "message": "كل سطر يجب أن يحتوي على `product_id` و `product_uom_qty`"}, 400

            order_lines.append((0, 0, {
                'product_id': int(line.get('product_id')),
                'product_uom_qty': line.get('product_uom_qty'),
                'discount': line.get('discount', 0),
            }))

        # 🔹 تحديد `company_id`
        company_id = data.get('company_id') or user.company_id.id
        if not company_id:
            return {"success": False, "message": "يجب تحديد `company_id`"}, 400

        # 🔹 إنشاء أمر البيع
        try:
            sale_order = request.env['sale.order'].sudo().create({
                'partner_id': data.get('partner_id'),
                'pricelist_id': data.get('pricelist_id'),
                'user_id': user.id,  # 🔹 استخدام `user.id` الصحيح
                'date_order': data.get('date_order'),
                'company_id': company_id,
                'order_line': order_lines,
            })

            return {
                "success": True,
                "message": "تم إنشاء أمر البيع بنجاح",
                "order_id": sale_order.id,
                "order_name": sale_order.name
            }, 200

        except Exception as e:
            print(e)
            return {"success": False, "message": f"حدث خطأ أثناء إنشاء أمر البيع: {str(e)}"}, 500

    ###################### Create Sale Order3 ###########################ok
    @http.route("/api/sale/order", methods=["POST"], type="json", auth="none", csrf=False)
    def create_sale_order_api(self):
        # ✅ 1. استخراج الـ Token من الـ Header والتحقق منه
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_json_response({
                "success": False,
                "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"
            }, status=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = request.env['res.users'].sudo().browse(user_id)

            if not user.exists():
                return request.make_json_response({
                    "success": False,
                    "message": "المستخدم غير موجود"
                }, status=401)

        except jwt.ExpiredSignatureError:
            return request.make_json_response({
                "success": False,
                "message": "انتهت صلاحية Token"
            }, status=401)
        except jwt.InvalidTokenError:
            return request.make_json_response({
                "success": False,
                "message": "Token غير صالح"
            }, status=401)

        print("inside create sale order")

    ###################### Create Sale Order4 ###########################ok
    @http.route('/api/create_sales_order', type='json', auth="public", methods=['POST'])
    def create_so(self, **kw):

        # ✅ 1. استخراج الـ Token من الـ Header والتحقق منه
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_json_response({
                "success": False,
                "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"
            }, status=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = request.env['res.users'].sudo().browse(user_id)

            if not user.exists():
                return request.make_json_response({
                    "success": False,
                    "message": "المستخدم غير موجود"
                }, status=401)

        except jwt.ExpiredSignatureError:
            return request.make_json_response({
                "success": False,
                "message": "انتهت صلاحية Token"
            }, status=401)
        except jwt.InvalidTokenError:
            return request.make_json_response({
                "success": False,
                "message": "Token غير صالح"
            }, status=401)

        # Validate request data
        required_fields = ["customer_id", "pricelist_id", "salesperson_id", "items"]
        for field in required_fields:
            if not kw.get(field):
                return {'status_code': 400, 'is_error': True, 'message': f"Missing required field: {field}",
                        'result_rpo': ''}

        for item in kw.get('items', []):
            if not all(key in item and item[key] for key in ["product_id", "quantity", "price"]):
                return {'status_code': 400, 'is_error': True, 'message': "Missing product details",
                        'result_rpo': ''}

        # Create sale order
        sale_order = request.env['sale.order'].sudo().create({
            "partner_id": int(kw['customer_id']),

            "pricelist_id": int(kw['pricelist_id']),
            "user_id": int(kw['salesperson_id']),
            "order_line": [
                (0, 0, {
                    "product_id": int(item['product_id']),
                    "name": item.get('product_name', ''),
                    "product_uom_qty": float(item['quantity']),
                    "price_unit": float(item['price']),
                    "product_uom": request.env['product.product'].sudo().browse(int(item['product_id'])).uom_id.id,
                })
                for item in kw['items']
            ]
        })

        print(sale_order)

        sale_order.action_confirm()
        for order in sale_order:
            for picking in order.picking_ids:
                if picking.state not in ['done', 'cancel']:
                    picking.action_confirm()  # Confirm the picking
                    picking.action_assign()  # Assign products to picking
                    picking.button_validate()  # Validate the picking

            order._create_invoices()

            for invoice in order.invoice_ids:

                if invoice.state == 'draft':
                    invoice.action_post()

                if invoice.amount_residual > 0:
                    payment_type_value = kw.get('payment_type')  # استلام قيمة payment_type من Postman

                    journal = request.env['account.journal'].sudo().search([
                        ('company_id', '=', order.company_id.id),
                        ('payment_type', '=', payment_type_value)  # البحث باستخدام payment_type
                    ], limit=1)

                    if not journal:
                        return {'status_code': 400, 'is_error': True,
                                'message': "No matching journal found for the given payment type",
                                'result_rpo': ''}

                    payment_register = request.env['account.payment.register'].sudo().with_context(
                        active_model='account.move',
                        active_ids=invoice.ids
                    ).create({
                        'journal_id': journal.id,  # استخدام `journal_id` الصحيح بناءً على `payment_type`
                        'amount': invoice.amount_residual,
                        'payment_date': fields.Date.today(),
                    })

                    payment_register.action_create_payments()




        return {'status_code': 200, 'is_error': False, 'message': 'Order created successfully',
                'result_rpo': [sale_order]}


    ###################### Create Invoice ###########################ok
    # @http.route("/api/create/invoice", methods=["POST"], type="json", auth="none", csrf=False)
    # def create_api_invoice(self, **kw):
    #     # ✅ 1. استخراج الـ Token والتحقق منه
    #     auth_header = request.httprequest.headers.get('Authorization')
    #     if not auth_header or not auth_header.startswith('Bearer '):
    #         return request.make_json_response(
    #             {"success": False, "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"}, status=401)
    #
    #     token = auth_header.split(" ")[1]
    #     try:
    #         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    #         user_id = payload.get("user_id")
    #         user = request.env['res.users'].sudo().browse(user_id)
    #         request.env.user = user
    #         if not user.exists():
    #             return request.make_json_response({
    #                 "success": False,
    #                 "message": "المستخدم غير موجود"
    #             }, status=401)
    #     except jwt.ExpiredSignatureError:
    #         return request.make_json_response({"success": False, "message": "انتهت صلاحية Token"}, status=401)
    #     except jwt.InvalidTokenError:
    #         return request.make_json_response({"success": False, "message": "Token غير صالح"}, status=401)
    #
    #     print("🔹 Helllllo - Token verified!")
    #
    #     # ✅ 2. التحقق من جميع الحقول المطلوبة
    #     kw = request.httprequest.get_json()
    #     required_fields = ["partner_id", "move_type", "invoice_date", "journal_id"]
    #     for field in required_fields:
    #         if not kw.get(field):
    #             return request.make_json_response({"success": False, "message": f"Missing required field: {field}"},
    #                                               status=400)
    #
    #     print("1️⃣ - جميع الحقول المطلوبة متوفرة")
    #
    #     # try:
    #         # ✅ 3. التحقق من البيانات المرتبطة بالفاتورة
    #     partner = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
    #     if not partner.exists():
    #         return request.make_json_response({"success": False, "message": "الشريك غير موجود"}, status=400)
    #
    #     journal = request.env['account.journal'].sudo().browse(int(kw['journal_id']))
    #     if not journal.exists():
    #         return request.make_json_response({"success": False, "message": "دفتر اليومية غير موجود"},
    #                                           status=400)
    #
    #     company_id = user.company_id.id
    #     if not company_id:
    #         return request.make_json_response({"success": False, "message": "لا يوجد شركة مخصصة لهذا المستخدم"},
    #                                           status=400)
    #
    #     currency = user.company_id.currency_id
    #     if not currency.exists():
    #         return request.make_json_response({"success": False, "message": "العملة غير معرفة"}, status=400)
    #
    #     print("2️⃣ - التحقق من البيانات المرتبطة بالفاتورة")
    #
    #     # ✅ 4. تجهيز بيانات الفاتورة
    #     invoice_data = {
    #         "partner_id": partner.id,
    #         "move_type": kw['move_type'],
    #         "invoice_date": kw['invoice_date'],
    #         "company_id": company_id,
    #         "currency_id": currency.id,
    #         "journal_id": journal.id,
    #         "invoice_line_ids": []
    #     }
    #
    #     for item in kw['invoice_line_ids']:
    #         product = request.env['product.product'].sudo().search([('id', '=', int(item['product_id']))])
    #         if not product.exists():
    #             return [{"success": False, "message": f"المنتج غير موجود: {item['product_id']}"}]
    #
    #         # # 🔹 جلب الحساب المحاسبي من المنتج أو الفئة
    #         # account_id = product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id
    #         # if not account_id:
    #         #     return [{"success": False, "message": f"لا يوجد حساب محاسبي لهذا المنتج: {item['product_id']}"}]
    #
    #         invoice_data["invoice_line_ids"].append((0, 0, {
    #             "product_id": product.id,
    #             "price_unit": float(item['price']) if item.get('price') else 0.0,
    #             "quantity": float(item['quantity']),
    #             "company_id": company_id,
    #             # "account_id": account_id,  # ✅ تحديد الحساب المحاسبي هنا
    #             "tax_ids": [(6, 0, product.taxes_id.ids)]  # ✅ إضافة الضرائب إذا كانت مطلوبة
    #         }))
    #
    #     print("3️⃣ - تجهيز بيانات الفاتورة")
    #     print(f"🚀 Final Invoice Data: {invoice_data}")
    #
    #     # ✅ 5. إنشاء الفاتورة
    #     invoice = request.env['account.move'].sudo().with_user(SUPERUSER_ID).create(invoice_data)
    #     invoice.action_post()
    #     print("✅ Invoice Created with ID:", invoice.id)
    #
    #     return {
    #         "success": True,
    #         "message": "Invoice created successfully",
    #         "invoice_id": invoice.id,
    #     }
    #
    #     # except Exception as e:
    #     #     import traceback
    #     #     error_details = traceback.format_exc()
    #     #     print(f"🚨 Error creating invoice: {error_details}")
    #     #     return request.make_json_response({
    #     #         "success": False,
    #     #         "message": f"Error creating invoice: {str(e)}",
    #     #         "error_details": error_details
    #     #     }, status=500)





    ###################### Create Invoice ###########################ok


    @http.route("/api/create/invoice", methods=["POST"], type="json", auth="none", csrf=False)
    def create_api_invoice(self, **kw):
        # ✅ 1. استخراج الـ Token والتحقق منه
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_json_response(
                {"success": False, "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"}, status=401)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = request.env['res.users'].sudo().browse(user_id)
            request.env.user = user
            if not user.exists():
                return request.make_json_response({
                    "success": False,
                    "message": "المستخدم غير موجود"
                }, status=401)
        except jwt.ExpiredSignatureError:
            return request.make_json_response({"success": False, "message": "انتهت صلاحية Token"}, status=401)
        except jwt.InvalidTokenError:
            return request.make_json_response({"success": False, "message": "Token غير صالح"}, status=401)

        print("🔹 Helllllo - Token verified!")
        # ✅ 2. التحقق من جميع الحقول المطلوبة
        kw = request.httprequest.get_json()
        required_fields = ["partner_id", "move_type", "invoice_date", "journal_id"]
        for field in required_fields:
            if not kw.get(field):
                return request.make_json_response({"success": False, "message": f"Missing required field: {field}"},
                                                  status=400)

        print("1️⃣ - جميع الحقول المطلوبة متوفرة")

    # try:
        # ✅ 3. التحقق من البيانات المرتبطة بالفاتورة
        partner = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
        if not partner.exists():
            return {"success": False, "message": "الشريك غير موجود"}
        print("request.env.company.name")

        journal = request.env['account.journal'].sudo().search([('id', '=', int(kw['journal_id']))])
        payment_journal = request.env['account.journal'].sudo().search(
            [('payment_type', '=', (kw['payment_type']))], limit=1)

        print(payment_journal)
        print(journal)

        if not journal:
            return {"success": False, "message": "دفتر اليومية غير موجود"}

        company_id = user.company_id.id
        if not company_id:
            return {"success": False, "message": "لا يوجد شركة مخصصة لهذا المستخدم"}

        currency = user.company_id.currency_id
        if not currency:
            return {"success": False, "message": "العملة غير معرفة"}

        print("2️⃣ - التحقق من البيانات المرتبطة بالفاتورة")

        # ✅ 4. تجهيز بيانات الفاتورة
        invoice_data = {
            "partner_id": partner.id,
            "move_type": kw['move_type'],
            "invoice_date": kw['invoice_date'],
            "company_id": company_id,
            "currency_id": currency.id,
            "journal_id": journal.id,
            "invoice_line_ids": []
        }

        for item in kw['invoice_line_ids']:
            product = request.env['product.product'].sudo().search([('id', '=', int(item['product_id']))])
            if not product.exists():
                return [{"success": False, "message": f"المنتج غير موجود: {item['product_id']}"}]

            invoice_data["invoice_line_ids"].append((0, 0, {
                "product_id": product.id,
                "price_unit": float(item['price']) if item.get('price') else 0.0,
                "quantity": float(item['quantity']),
                "company_id": company_id,
                # "account_id": account_id,  # ✅ تحديد الحساب المحاسبي هنا
                "tax_ids": [(6, 0, product.taxes_id.ids)]  # ✅ إضافة الضرائب إذا كانت مطلوبة
            }))

        print("3️⃣ - تجهيز بيانات الفاتورة")
        print(f"🚀 Final Invoice Data: {invoice_data}")
        invoice = request.env['account.move'].sudo().with_user(SUPERUSER_ID).create(invoice_data)

        # ✅ 5. إنشاء الفاتورة
        # invoice = request.env['account.move'].sudo().create(invoice_data)

        invoice.action_post()
        payment = request.env['account.payment'].sudo().create({
            'currency_id': invoice.currency_id.id,
            'amount': invoice.amount_residual,

            'payment_type': 'inbound',
            'partner_id': invoice.partner_id.id,
            'partner_type': 'customer',
            'ref': invoice.payment_reference or invoice.name,
            'journal_id': payment_journal.id,
            'company_id': 1
        })

        payment.action_post()
        line_id = payment.line_ids.filtered(lambda l: l.credit)
        invoice.js_assign_outstanding_line(line_id.id)

        print("✅ Invoice Created with ID:", invoice.id)

        return {
                "success": True,
                "message": "Invoice created successfully",
                "invoice_id": invoice.id,
            }



    # except Exception as e:
    #     import traceback
    #     error_details = traceback.format_exc()
    #     print(f"🚨 Error creating invoice: {error_details}")
    #     return request.make_json_response({
    #         "success": False,
    #         "message": f"Error creating invoice: {str(e)}",
    #         "error_details": error_details
    #     }, status=500)


    ###################### Create Product ###########################ok
    @http.route('/api/create_product', type='json', auth='user', methods=['POST'], csrf=False)
    def create_product(self, **kwargs):

        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_json_response(
                {"success": False, "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"}, status=401)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = request.env['res.users'].sudo().browse(user_id)
            request.env.user = user
            if not user.exists():
                return request.make_json_response({
                    "success": False,
                    "message": "المستخدم غير موجود"
                }, status=401)
        except jwt.ExpiredSignatureError:
            return request.make_json_response({"success": False, "message": "انتهت صلاحية Token"}, status=401)
        except jwt.InvalidTokenError:
            return request.make_json_response({"success": False, "message": "Token غير صالح"}, status=401)


        print("inside product")

        """
               API لإنشاء منتج جديد داخل `product.template`
               """

        data = request.httprequest.get_json()  # استلام البيانات المرسلة من Postman
        name = data.get('name')  # اسم المنتج
        price = data.get('price', 0.0)  # السعر الافتراضي 0 إذا لم يتم إرساله
        description = data.get('description', '')  # وصف المنتج
        product_type = data.get('type', 'consu')  # نوع المنتج (الافتراضي: منتج استهلاكي)

        # **🔍 تحقق من إدخال القيم المطلوبة**
        if not name or price is None:
            return {"success": False, "message": "الاسم والسعر مطلوبان"}

        # **🔍 تحقق من صحة نوع المنتج**
        valid_types = ['consu', 'service', 'product']
        if product_type not in valid_types:
            return {"success": False, "message": "نوع المنتج غير صحيح. القيم المسموح بها: consu, service, product"}

        # **🛠️ إنشاء المنتج في `product.template`**
        try:
            new_product = request.env['product.template'].sudo().create({
                'name': name,
                'list_price': price,  # السعر
                'description_sale': description,  # الوصف
                'type': product_type,  # نوع المنتج
            })

            return {
                "success": True,
                "message": "تم إنشاء المنتج بنجاح",
                "product_id": new_product.id,
                "type": new_product.type,
            }

        except Exception as e:
            _logger.error(f"Error creating product: {str(e)}")
            return {"success": False, "message": f"حدث خطأ: {str(e)}"}

    ###################### Create account ###########################ok
    @http.route('/api/create_account', type='json', auth='user', methods=['POST'], csrf=False)
    def create_account(self, **kwargs):

        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return request.make_json_response(
                {"success": False, "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"}, status=401)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = request.env['res.users'].sudo().browse(user_id)
            request.env.user = user
            if not user.exists():
                return request.make_json_response({
                    "success": False,
                    "message": "المستخدم غير موجود"
                }, status=401)
        except jwt.ExpiredSignatureError:
            return request.make_json_response({"success": False, "message": "انتهت صلاحية Token"}, status=401)
        except jwt.InvalidTokenError:
            return request.make_json_response({"success": False, "message": "Token غير صالح"}, status=401)

        print("inside account")

        """
                API لإنشاء حساب جديد داخل `account.account`
                """

        data = request.httprequest.get_json()  # استلام البيانات المرسلة من Postman
        name = data.get('name')  # اسم الحساب
        code = data.get('code')  # كود الحساب
        account_type = data.get('account_type')  # نوع الحساب
        company_id = data.get('company_id', 1)  # رقم الشركة (افتراضي 1)

        # **🔍 تحقق من إدخال القيم المطلوبة**
        if not name or not code or not account_type:
            return {"success": False, "message": "الاسم، الكود، ونوع الحساب مطلوبة"}

        # **🔍 تحقق من صحة نوع الحساب**
        valid_types = ['asset', 'liability', 'income', 'expense', 'equity']
        if account_type not in valid_types:
            return {"success": False,
                    "message": "نوع الحساب غير صحيح. القيم المسموح بها: asset, liability, income, expense, equity"}

        # **🛠️ إنشاء الحساب في `account.account`**
        try:
            new_account = request.env['account.account'].sudo().create({
                'name': name,
                'code': code,
                'account_type': account_type,  # نوع الحساب
                'company_id': company_id,
            })

            return {
                "success": True,
                "message": "تم إنشاء الحساب بنجاح",
                "account_id": new_account.id,
                "account_type": new_account.account_type,
            }

        except Exception as e:
            _logger.error(f"Error creating account: {str(e)}")
            return {"success": False, "message": f"حدث خطأ: {str(e)}"}




