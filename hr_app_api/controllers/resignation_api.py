from odoo import http, fields
from odoo.http import request
from .main import decode_token  # تستورد من ملفك الحالي

class ResignationAPI(http.Controller):

    @http.route('/api/resignations', type='json', auth='public', methods=['POST'], csrf=False)
    def submit_resignation(self, **kwargs):
        # ✅ قراءة التوكن من الهيدر
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'message': 'Missing Authorization token'}

        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        payload = decode_token(token)

        if not payload:
            return {'success': False, 'message': 'Invalid or expired token'}

        user_id = payload.get('user_id')
        user = request.env['res.users'].sudo().browse(user_id)
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return {'success': False, 'message': 'No employee record linked to this user'}

        reason = kwargs.get('reason')
        resignation_date = kwargs.get('resignation_date') or fields.Date.today()

        if not reason:
            return {'success': False, 'message': 'Missing resignation reason'}

        resignation = request.env['hr.resignation'].sudo().create({
            'employee_id': employee.id,
            'reason': reason,
            'resignation_date': resignation_date,
        })

        return {
            'success': True,
            'resignation_id': resignation.id,
            'message': 'Resignation submitted successfully'
        }
