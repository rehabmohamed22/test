# -*- coding: utf-8 -*-
# from odoo import http


# class StockScrapMultiProduct(http.Controller):
#     @http.route('/stock_scrap_multi_product/stock_scrap_multi_product', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_scrap_multi_product/stock_scrap_multi_product/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_scrap_multi_product.listing', {
#             'root': '/stock_scrap_multi_product/stock_scrap_multi_product',
#             'objects': http.request.env['stock_scrap_multi_product.stock_scrap_multi_product'].search([]),
#         })

#     @http.route('/stock_scrap_multi_product/stock_scrap_multi_product/objects/<model("stock_scrap_multi_product.stock_scrap_multi_product"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_scrap_multi_product.object', {
#             'object': obj
#         })

