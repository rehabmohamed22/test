# -*- coding: utf-8 -*-
# from odoo import http


# class ElearningInvoice(http.Controller):
#     @http.route('/elearning_invoice/elearning_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/elearning_invoice/elearning_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('elearning_invoice.listing', {
#             'root': '/elearning_invoice/elearning_invoice',
#             'objects': http.request.env['elearning_invoice.elearning_invoice'].search([]),
#         })

#     @http.route('/elearning_invoice/elearning_invoice/objects/<model("elearning_invoice.elearning_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('elearning_invoice.object', {
#             'object': obj
#         })

