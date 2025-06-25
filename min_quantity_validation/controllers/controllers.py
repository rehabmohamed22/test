# -*- coding: utf-8 -*-
# from odoo import http


# class MinQuantityValidation(http.Controller):
#     @http.route('/min_quantity_validation/min_quantity_validation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/min_quantity_validation/min_quantity_validation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('min_quantity_validation.listing', {
#             'root': '/min_quantity_validation/min_quantity_validation',
#             'objects': http.request.env['min_quantity_validation.min_quantity_validation'].search([]),
#         })

#     @http.route('/min_quantity_validation/min_quantity_validation/objects/<model("min_quantity_validation.min_quantity_validation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('min_quantity_validation.object', {
#             'object': obj
#         })

