# -*- coding: utf-8 -*-
# from odoo import http


# class NafisIntegration(http.Controller):
#     @http.route('/nafis_integration/nafis_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nafis_integration/nafis_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nafis_integration.listing', {
#             'root': '/nafis_integration/nafis_integration',
#             'objects': http.request.env['nafis_integration.nafis_integration'].search([]),
#         })

#     @http.route('/nafis_integration/nafis_integration/objects/<model("nafis_integration.nafis_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nafis_integration.object', {
#             'object': obj
#         })

