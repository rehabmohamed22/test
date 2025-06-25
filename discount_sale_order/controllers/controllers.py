# -*- coding: utf-8 -*-
# from odoo import http


# class DiscountSaleOrder(http.Controller):
#     @http.route('/discount_sale_order/discount_sale_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/discount_sale_order/discount_sale_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('discount_sale_order.listing', {
#             'root': '/discount_sale_order/discount_sale_order',
#             'objects': http.request.env['discount_sale_order.discount_sale_order'].search([]),
#         })

#     @http.route('/discount_sale_order/discount_sale_order/objects/<model("discount_sale_order.discount_sale_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('discount_sale_order.object', {
#             'object': obj
#         })

