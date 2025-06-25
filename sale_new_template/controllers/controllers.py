# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseNewTemplate(http.Controller):
#     @http.route('/purchase_new_template/purchase_new_template', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_new_template/purchase_new_template/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_new_template.listing', {
#             'root': '/purchase_new_template/purchase_new_template',
#             'objects': http.request.env['purchase_new_template.purchase_new_template'].search([]),
#         })

#     @http.route('/purchase_new_template/purchase_new_template/objects/<model("purchase_new_template.purchase_new_template"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_new_template.object', {
#             'object': obj
#         })

