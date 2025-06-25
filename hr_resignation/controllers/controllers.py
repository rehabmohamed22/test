# -*- coding: utf-8 -*-
# from odoo import http


# class HrResignation(http.Controller):
#     @http.route('/hr_resignation/hr_resignation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_resignation/hr_resignation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_resignation.listing', {
#             'root': '/hr_resignation/hr_resignation',
#             'objects': http.request.env['hr_resignation.hr_resignation'].search([]),
#         })

#     @http.route('/hr_resignation/hr_resignation/objects/<model("hr_resignation.hr_resignation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_resignation.object', {
#             'object': obj
#         })

