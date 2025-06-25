# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceAmountCustomerValidation(http.Controller):
#     @http.route('/invoice_amount_customer_validation/invoice_amount_customer_validation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_amount_customer_validation/invoice_amount_customer_validation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_amount_customer_validation.listing', {
#             'root': '/invoice_amount_customer_validation/invoice_amount_customer_validation',
#             'objects': http.request.env['invoice_amount_customer_validation.invoice_amount_customer_validation'].search([]),
#         })

#     @http.route('/invoice_amount_customer_validation/invoice_amount_customer_validation/objects/<model("invoice_amount_customer_validation.invoice_amount_customer_validation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_amount_customer_validation.object', {
#             'object': obj
#         })

