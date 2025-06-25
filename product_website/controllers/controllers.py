# -*- coding: utf-8 -*-
# from odoo import http


# class ProductWebsite(http.Controller):
#     @http.route('/product_website/product_website', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_website/product_website/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_website.listing', {
#             'root': '/product_website/product_website',
#             'objects': http.request.env['product_website.product_website'].search([]),
#         })

#     @http.route('/product_website/product_website/objects/<model("product_website.product_website"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_website.object', {
#             'object': obj
#         })

