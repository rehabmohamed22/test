# -*- coding: utf-8 -*-
# from odoo import http


# class HrAppApi(http.Controller):
#     @http.route('/hr_app_api/hr_app_api', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_app_api/hr_app_api/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_app_api.listing', {
#             'root': '/hr_app_api/hr_app_api',
#             'objects': http.request.env['hr_app_api.hr_app_api'].search([]),
#         })

#     @http.route('/hr_app_api/hr_app_api/objects/<model("hr_app_api.hr_app_api"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_app_api.object', {
#             'object': obj
#         })

