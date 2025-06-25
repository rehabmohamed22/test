# -*- coding: utf-8 -*-
# from odoo import http


# class JofalProductDistribution(http.Controller):
#     @http.route('/jofal_product_distribution/jofal_product_distribution', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jofal_product_distribution/jofal_product_distribution/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jofal_product_distribution.listing', {
#             'root': '/jofal_product_distribution/jofal_product_distribution',
#             'objects': http.request.env['jofal_product_distribution.jofal_product_distribution'].search([]),
#         })

#     @http.route('/jofal_product_distribution/jofal_product_distribution/objects/<model("jofal_product_distribution.jofal_product_distribution"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jofal_product_distribution.object', {
#             'object': obj
#         })

