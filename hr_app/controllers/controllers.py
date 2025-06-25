import logging
import json
import re
from functools import wraps
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


def valid_response(data, status, pagination_info=None):
    response_body = {
        'data': data,
        'message': "successfil",
    }
    if pagination_info:
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(response_body, status=status)


class productApi(http.Controller):

    def get_allowed_fields(self, fetch_id):

        return [rec.name for rec in fetch_id.fields_api]


    #########################  Register ######################
    @http.route('/api/hr/register', type='json', auth='public', methods=['POST'], csrf=False)
    def register(self, **kwargs):
        """ تسجيل مستخدم جديد وإنشاء موظف مرتبط """
        try:
            data = request.httprequest.get_json()
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            # ✅ تحقق من البيانات الأساسية
            if not name or not email or not password:
                return {"success": False, "message": "الاسم، البريد الإلكتروني، وكلمة المرور مطلوبة"}

            # ✅ تحقق من صحة البريد الإلكتروني
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, email):
                return {"success": False, "message": "يرجى إدخال بريد إلكتروني صحيح"}

            # ✅ تحقق من عدم وجود مستخدم مسبقًا
            existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if existing_user:
                return {"success": False, "message": "البريد الإلكتروني مستخدم بالفعل"}

            # ✅ الحصول على مجموعة portal
            portal_group = request.env.ref('base.group_portal')

            # ✅ إنشاء المستخدم وتعيينه لمجموعة portal فقط
            user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'email': email,
                'password': password,
                'groups_id': [(6, 0, [portal_group.id])]
            })

            # ✅ إنشاء الموظف المرتبط بالمستخدم
            employee = request.env['hr.employee'].sudo().create({
                'name': name,
                'user_id': user.id,
                'work_email': email,
                'image_1920': user.image_1920,
            })

            # ✅ ربط المستخدم بالموظف (العكس)
            user.sudo().write({'employee_id': employee.id})

            return {
                "success": True,
                "message": "تم تسجيل المستخدم وإنشاء الموظف بنجاح",
                "user_id": user.id,
                "employee_id": employee.id
            }

        except Exception as e:
            return {"success": False, "message": f"خطأ في السيرفر: {str(e)}"}

    #########################  Login ######################
    @http.route('/api/hr/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        try:
            data = request.httprequest.get_json()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {"success": False, "message": "جميع الحقول مطلوبة"}

            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if not user:
                return {"success": False, "message": "المستخدم غير موجود"}

            try:
                uid = request.session.authenticate(request.db, email, password)
            except AccessDenied:
                return {"success": False, "message": "كلمة المرور غير صحيحة"}

            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            payload = {
                "user_id": user.id,
                "email": email,
                "exp": expiration
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            # 🧹 حذف التوكنات السابقة لهذا المستخدم
            request.env['auth.token'].sudo().search([('user_id', '=', user.id)]).unlink()

            # 💾 حفظ التوكن الجديد
            request.env['auth.token'].sudo().create({
                'user_id': user.id,
                'token': token,
                'expiration': expiration
            })

            return {
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "user_id": user.id,
                "token": token
            }

        except Exception as e:
            _logger.error(f"Login error: {str(e)}")
            return {"success": False, "message": f"خطأ داخلي في السيرفر: {str(e)}"}


    ######################################################### Check Token * Decorator * ##################################
    def jwt_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.httprequest.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return request.make_json_response({
                    "success": False,
                    "message": "يجب إرسال Token في Authorization Header بصيغة Bearer"
                }, status=401)

            token = auth_header.split(" ")[1]

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")

                user = request.env["res.users"].sudo().browse(user_id)
                if not user.exists():
                    return request.make_json_response({
                        "success": False,
                        "message": "المستخدم غير موجود"
                    }, status=401)

                token_record = request.env['auth.token'].sudo().search([
                    ('user_id', '=', user.id),
                    ('token', '=', token)
                ], limit=1)

                if not token_record:
                    return request.make_json_response({
                        "success": False,
                        "message": "Token غير مسموح به أو تم تسجيل الدخول بعده"
                    }, status=401)

                # ✅ تخزين المستخدم في request للوصول إليه لاحقًا
                request.current_user = user
                return func(*args, **kwargs)

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
            except Exception as e:
                return request.make_json_response({
                    "success": False,
                    "message": f"خطأ أثناء التحقق من التوكن: {str(e)}"
                }, status=401)

        return wrapper

    #########################  Logout ######################
    @http.route('/api/hr/logout', type='http', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def logout(self):
        auth_header = request.httprequest.headers.get('Authorization')
        token = auth_header.split(" ")[1]

        user = request.current_user

        # حذف التوكن من الجدول
        token_record = request.env['auth.token'].sudo().search([
            ('user_id', '=', user.id),
            ('token', '=', token)
        ], limit=1)

        if token_record:
            token_record.unlink()

        return request.make_json_response({
            "success": True,
            "message": "تم تسجيل الخروج بنجاح"
        }, status=200)

    ######################## collection * Decorator * ###########################ok
    @http.route("/v1/collection/data", methods=["GET"], type="http", auth="none", csrf=False)
    @jwt_required
    def get_collection_data(self):
        user = request.current_user  # ✅ المستخدم تم استخراجه تلقائيًا من التوكن

        params = parse_qs(request.httprequest.query_string.decode('utf-8'))
        product_domain = []
        page = offset = None
        limit = 5
        model = params.get('model')

        model = model[0] if model else ''
        if model:
            fetch_id = request.env['fetch.data'].sudo().search([('model_name', '=', model)])
        else:
            fetch_id = request.env['fetch.data']

        fields = self.get_allowed_fields(fetch_id)

        if params:
            if params.get('limit'):
                limit = int(params.get('limit')[0])
            if params.get('page'):
                page = int(params.get('page')[0])
        if page:
            offset = (page * limit) - limit

        if not fetch_id:
            return request.make_json_response("model not allowed", status=400)

        data = request.env[model].sudo().search_read(fields=fields, offset=offset, limit=limit, order='id desc')

        if not data:
            return request.make_json_response({
                "error": "There are not records!",
            }, status=400)

        return valid_response(
            data,
            pagination_info={
                'page': page if page else 1,
                'limit': limit,
            },
            status=200
        )

    #########################   Create Attendance  ################################################
    @http.route('/api/hr/attendance/create', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def create_attendance(self, **kwargs):
        """ إنشاء سجل حضور أو انصراف """
        try:
            user = request.current_user
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            print("🎯 Found employee:", employee.id, employee.name)

            if not employee:
                return {"success": False, "message": "المستخدم غير مرتبط بأي موظف"}

            data = request.get_json_data()
            check_type = data.get('type')  # 'check_in' أو 'check_out'

            if check_type not in ['check_in', 'check_out']:
                return {"success": False, "message": "القيمة type يجب أن تكون check_in أو check_out"}

            if check_type == 'check_in':
                attendance = request.env['hr.attendance'].sudo().create({
                    'employee_id': employee.id,
                    'check_in': fields.Datetime.now()
                })
                return {
                    "success": True,
                    "message": "تم تسجيل الحضور بنجاح",
                    "attendance_id": attendance.id
                }

            else:  # check_out
                last_attendance = request.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False)
                ], order='check_in desc', limit=1)

                if not last_attendance:
                    return {"success": False, "message": "لا يوجد حضور لتسجيل انصراف له"}

                last_attendance.write({
                    'check_out': fields.Datetime.now()
                })
                return {
                    "success": True,
                    "message": "تم تسجيل الانصراف بنجاح",
                    "attendance_id": last_attendance.id
                }

        except Exception as e:
            return {"success": False, "message": f"خطأ في السيرفر: {str(e)}"}

    #########################   Create TimeOff  ################################################
    @http.route('/api/hr/leave/create', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def create_leave(self, **kwargs):
        try:
            user = request.current_user
            data = request.get_json_data()

            # ✅ استخراج الموظف المرتبط بالمستخدم الحالي
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            # ✅ استخراج البيانات من الطلب (بدون employee_id)
            holiday_status_id = data.get('holiday_status_id')
            date_from = data.get('request_date_from')
            date_to = data.get('request_date_to')
            reason = data.get('name')

            # ✅ التحقق من البيانات المطلوبة
            if not all([holiday_status_id, date_from, date_to, reason]):
                return {
                    "success": False,
                    "message": "كل من الحقول التالية مطلوب: holiday_status_id, request_date_from, request_date_to, name"
                }

            # ✅ إنشاء طلب الإجازة
            leave = request.env['hr.leave'].sudo().create({
                'employee_id': employee.id,
                'holiday_status_id': holiday_status_id,
                'request_date_from': date_from,
                'request_date_to': date_to,
                'name': reason,
            })

            return {
                "success": True,
                "message": "تم إنشاء طلب الإجازة بنجاح",
                "leave_id": leave.id
            }

        except Exception as e:
            return {"success": False, "message": f"خطأ في السيرفر: {str(e)}"}

    ########################   Resignation  #####################################################
    @http.route('/api/hr/resignation/create', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def create_resignation(self, **kwargs):
        try:
            user = request.current_user
            data = request.get_json_data()

            # ✅ البحث عن الموظف المرتبط بالمستخدم
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            # ✅ قراءة باقي البيانات
            resignation_date = data.get('resignation_date')
            reason = data.get('reason')
            resignation_type = data.get('resignation_type')

            # ✅ التحقق من البيانات المطلوبة
            if not all([resignation_date, reason, resignation_type]):
                return {
                    "success": False,
                    "message": "جميع الحقول التالية مطلوبة: resignation_date, reason, resignation_type"
                }

            # ✅ التحقق من نوع الاستقالة
            allowed_types = [
                'voluntary', 'forced', 'with_cause', 'immediate',
                'with_notice', 'retirement', 'mutual'
            ]

            if resignation_type not in allowed_types:
                return {
                    "success": False,
                    "message": "نوع الاستقالة غير صالح"
                }

            # ✅ إنشاء سجل الاستقالة
            resignation = request.env['hr.resignation'].sudo().create({
                'employee_id': employee.id,
                'resignation_date': resignation_date,
                'reason': reason,
                'resignation_type': resignation_type,
            })

            return {
                "success": True,
                "message": "تم تقديم طلب الاستقالة بنجاح",
                "resignation_id": resignation.id
            }

        except Exception as e:
            return {"success": False, "message": f"خطأ في السيرفر: {str(e)}"}

    ########################   Profile  #####################################################
    @http.route('/api/hr/profile', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def get_user_profile(self):
        try:
            user = request.current_user

            # ✅ البحث عن الموظف المرتبط
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            profile_data = {
                "user_id": user.id,
                "employee_id": employee.id,
                "name": user.name,
                "email": user.login,
                "job_title": employee.job_title,
                "department": employee.department_id.name if employee.department_id else None,
                "manager": employee.parent_id.name if employee.parent_id else None,
                "image_1920": f"/web/image?model=res.users&id={user.id}&field=image_1920"
            }

            return {
                "success": True,
                "data": profile_data
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في السيرفر: {str(e)}"
            }

    ########################   Status TimeOff for Employee  #####################################################
    @http.route('/api/hr/leaves', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def get_employee_leaves(self, **kwargs):
        try:
            user = request.current_user

            # ✅ البحث عن الموظف المرتبط بالمستخدم
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            # ✅ البحث عن طلبات الإجازة
            leave_requests = request.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee.id)
            ], order="request_date_from desc")

            if not leave_requests:
                return {
                    "success": True,
                    "message": "لا توجد طلبات إجازة لهذا الموظف",
                    "leaves": []
                }

            result = []
            for leave in leave_requests:
                result.append({
                    "leave_id": leave.id,
                    "holiday_status": leave.holiday_status_id.name,
                    "request_date_from": leave.request_date_from,
                    "request_date_to": leave.request_date_to,
                    "number_of_days": leave.number_of_days_display,
                    "state": leave.state,
                    "reason": leave.name,
                    "manager": leave.manager_id.name if leave.manager_id else None,
                })

            return {
                "success": True,
                "leaves": result
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في السيرفر: {str(e)}"
            }

#########################################expenses#####################################################
    @http.route('/api/hr/expenses/create', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def create_expense(self, **kwargs):
        try:
            user = request.current_user
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)


            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            data = request.get_json_data()
            name = data.get('name')
            amount = data.get('amount')
            product_id = data.get('product_id')

            description = data.get('description', '')
            date = data.get('date') or fields.Date.today()

            if not name or not amount:
                return {
                    "success": False,
                    "message": "يجب إدخال الاسم والمبلغ"
                }

            company = request.env['res.company'].sudo().browse(user.company_id.id)
            currency = company.currency_id.id

            expense = request.env['hr.expense'].sudo().create({
                'name': name,
                'total_amount': amount,
                'product_id': product_id,
                'description': description,
                'employee_id': employee.id,
                'date': date,
                'company_id': company.id,  # ✅ نحدد الشركة بوضوح
                'currency_id': currency,  # ✅ ونستخرج العملة منها مباشرة
                'state': 'draft'
            })

            return {
                "success": True,
                "message": "تم إنشاء المصروف بنجاح",
                "expense_id": expense.id
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في السيرفر: {str(e)}"
            }
########################################get_expenses########################################################

    @http.route('/api/hr/expenses', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def get_expenses(self, **kwargs):
        try:
            user = request.current_user
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            expenses = request.env['hr.expense'].sudo().search([
                ('employee_id', '=', employee.id)
            ], order="date desc")

            data = []
            for exp in expenses:
                data.append({
                    "expense_id": exp.id,
                    "name": exp.name,
                    "amount": exp.total_amount,
                    "date": str(exp.date),
                    "status": exp.state,  # draft / reported / approved / refused / done
                    "description": exp.description,
                })

            return {
                "success": True,
                "expenses": data
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في السيرفر: {str(e)}"
            }
####################################    Create_Expenses    #####################################################
    @http.route('/api/hr/expenses/create', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def create_expense(self, **kwargs):
        try:
            user = request.current_user
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            data = request.get_json_data()
            name = data.get('name')
            amount = data.get('amount')
            product_id = data.get('product_id')
            description = data.get('description', '')
            date = data.get('date') or fields.Date.today()

            # تحقق من البيانات الأساسية
            if not name or not amount or not product_id:
                return {"success": False, "message": "يجب إدخال الاسم والمبلغ ونوع المصروف"}

            company = request.env['res.company'].sudo().browse(user.company_id.id)
            currency = company.currency_id.id

            expense = request.env['hr.expense'].sudo().create({
                'name': name,
                'total_amount': amount,
                'product_id': product_id,
                'description': description,
                'employee_id': employee.id,
                'date': date,
                'company_id': company.id,  # ✅ نحدد الشركة بوضوح
                'currency_id': currency,  # ✅ ونستخرج العملة منها مباشرة
                'state': 'draft'
            })

            return {
                "success": True,
                "message": "تم إنشاء المصروف بنجاح",
                "expense_id": expense.id
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في السيرفر: {str(e)}"
            }

    ####################################   Get_Expenses   ###################################################
    @http.route('/api/hr/expenses', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def get_expenses(self, **kwargs):
        try:
            user = request.current_user
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            expenses = request.env['hr.expense'].sudo().search([
                ('employee_id', '=', employee.id)
            ], order="date desc")

            data = []
            for exp in expenses:
                data.append({
                    "expense_id": exp.id,
                    "name": exp.name,
                    "amount": exp.total_amount,
                    "date": str(exp.date),
                    "status": exp.state,  # draft / reported / approved / refused / done
                    "description": exp.description,
                })

            return {
                "success": True,
                "expenses": data
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في السيرفر: {str(e)}"
            }

    ####################################   Get_Payslip   ###################################################
    @http.route('/api/hr/payslip', type='json', auth='none', methods=['POST'], csrf=False)
    @jwt_required
    def get_payslip(self, **kwargs):
        try:
            user = request.current_user
            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

            if not employee:
                return {
                    "success": False,
                    "message": "المستخدم غير مرتبط بأي موظف"
                }

            # جلب أحدث قسيمة راتب للموظف
            payslip = request.env['hr.payslip'].sudo().search(
                [('employee_id', '=', employee.id)],
                order='date_to desc',
                limit=1
            )

            if not payslip:
                return {
                    "success": False,
                    "message": "لا توجد قسائم راتب لهذا الموظف"
                }

            result_lines = []
            for line in payslip.line_ids:
                result_lines.append({
                    'name': line.name,
                    'code': line.code,
                    'category': line.category_id.name if line.category_id else '',
                    'amount': line.total
                })

            return {
                "success": True,
                "payslip_id": payslip.id,
                "employee_name": employee.name,
                "date_from": payslip.date_from,
                "date_to": payslip.date_to,
                "state": payslip.state,
                "lines": result_lines,
                "net": payslip.net_wage,
                "gross": payslip.gross_wage
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في السيرفر: {str(e)}"
            }