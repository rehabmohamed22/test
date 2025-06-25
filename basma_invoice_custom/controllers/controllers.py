# -*- coding: utf-8 -*-
# from odoo import http


# class BasmaInvoiceCustom(http.Controller):
#     @http.route('/basma_invoice_custom/basma_invoice_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/basma_invoice_custom/basma_invoice_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('basma_invoice_custom.listing', {
#             'root': '/basma_invoice_custom/basma_invoice_custom',
#             'objects': http.request.env['basma_invoice_custom.basma_invoice_custom'].search([]),
#         })

#     @http.route('/basma_invoice_custom/basma_invoice_custom/objects/<model("basma_invoice_custom.basma_invoice_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('basma_invoice_custom.object', {
#             'object': obj
#         })

