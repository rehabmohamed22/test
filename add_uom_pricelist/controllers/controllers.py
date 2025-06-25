# -*- coding: utf-8 -*-
# from odoo import http


# class AddUomPricelist(http.Controller):
#     @http.route('/add_uom_pricelist/add_uom_pricelist', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_uom_pricelist/add_uom_pricelist/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_uom_pricelist.listing', {
#             'root': '/add_uom_pricelist/add_uom_pricelist',
#             'objects': http.request.env['add_uom_pricelist.add_uom_pricelist'].search([]),
#         })

#     @http.route('/add_uom_pricelist/add_uom_pricelist/objects/<model("add_uom_pricelist.add_uom_pricelist"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_uom_pricelist.object', {
#             'object': obj
#         })

