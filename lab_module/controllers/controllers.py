# -*- coding: utf-8 -*-
# from odoo import http


# class LabModule(http.Controller):
#     @http.route('/lab_module/lab_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lab_module/lab_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('lab_module.listing', {
#             'root': '/lab_module/lab_module',
#             'objects': http.request.env['lab_module.lab_module'].search([]),
#         })

#     @http.route('/lab_module/lab_module/objects/<model("lab_module.lab_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lab_module.object', {
#             'object': obj
#         })

