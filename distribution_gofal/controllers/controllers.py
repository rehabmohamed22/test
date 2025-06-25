# -*- coding: utf-8 -*-
# from odoo import http


# class DistributionGofal(http.Controller):
#     @http.route('/distribution_gofal/distribution_gofal', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/distribution_gofal/distribution_gofal/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('distribution_gofal.listing', {
#             'root': '/distribution_gofal/distribution_gofal',
#             'objects': http.request.env['distribution_gofal.distribution_gofal'].search([]),
#         })

#     @http.route('/distribution_gofal/distribution_gofal/objects/<model("distribution_gofal.distribution_gofal"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('distribution_gofal.object', {
#             'object': obj
#         })

