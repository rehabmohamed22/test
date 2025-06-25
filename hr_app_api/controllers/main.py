from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
import jwt
import datetime
import re

SECRET_KEY = "MY_SECRET_KEY"  # يفضل later يكون في config/env


def generate_token(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_token(token):
    try:
        blacklisted = request.env['jwt.token.blacklist'].sudo().search([('token', '=', token)], limit=1)
        if blacklisted:
            return None  # التوكن تم تسجيل خروجه

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class HRAppAPIController(http.Controller):

    # -------------------- Register --------------------
    @http.route('/api/register', type='json', auth='public', methods=['POST'], csrf=False)
    def register(self, **kwargs):
        data = request.httprequest.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return {"success": False, "message": "يرجى إدخال الاسم والبريد وكلمة المرور"}

        # تحقق من صحة الإيميل
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "message": "البريد الإلكتروني غير صالح"}

        # تحقق إن المستخدم مش موجود بالفعل
        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return {"success": False, "message": "هذا المستخدم موجود بالفعل"}

        # إنشاء مستخدم جديد
        new_user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'email': email,
            'password': password,
        })

        return {
            "success": True,
            "message": "تم إنشاء المستخدم بنجاح",
            "user_id": new_user.id
        }

    # -------------------- Login --------------------
    @http.route('/api/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        data = request.httprequest.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {"success": False, "message": "يرجى إدخال البريد وكلمة المرور"}

        user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if not user:
            return {"success": False, "message": "المستخدم غير موجود"}

        try:
            uid = request.session.authenticate(request.db, email, password)
        except AccessDenied:
            return {"success": False, "message": "كلمة المرور غير صحيحة"}

        token = generate_token(user.id, email)
        return {
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "token": token,
            "user_id": user.id,
            "name": user.name
        }

    # -------------------- Logout (تطبيقي فقط) --------------------
    @http.route('/api/logout', type='json', auth='public', methods=['POST'], csrf=False)
    def logout(self, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            return {"success": False, "message": "لم يتم إرسال التوكن"}

        token = auth_header.split(" ")[1] if " " in auth_header else auth_header

        # تحقق إذا كان التوكن بالفعل محظور
        already_blacklisted = request.env['jwt.token.blacklist'].sudo().search([('token', '=', token)], limit=1)
        if already_blacklisted:
            return {"success": False, "message": "تم تسجيل الخروج مسبقًا"}

        # إضافة التوكن إلى الـ blacklist
        request.env['jwt.token.blacklist'].sudo().create({'token': token})

        return {
            "success": True,
            "message": "تم تسجيل الخروج بنجاح وتم تعطيل التوكن"
        }

class HRAppEmployeeAPI(http.Controller):

    @http.route('/api/employees', type='http', auth='public', methods=['GET'], csrf=False)
    def get_employees(self):
        employees = request.env['hr.employee'].sudo().search([])


        data = []
        for emp in employees:
            data.append({
                'id': emp.id,
                'name': emp.name,
                'email': emp.work_email or emp.user_id.login,
                'user_id': emp.user_id.id,
            })

        return request.make_json_response({
            "success": True,
            "data": data,
            "message": "تم جلب الموظفين بنجاح"
        }, status=200)