# -*- coding: utf-8 -*-
# from odoo import http


# class HelpdeskApi(http.Controller):
#     @http.route('/helpdesk_api/helpdesk_api', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/helpdesk_api/helpdesk_api/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('helpdesk_api.listing', {
#             'root': '/helpdesk_api/helpdesk_api',
#             'objects': http.request.env['helpdesk_api.helpdesk_api'].search([]),
#         })

#     @http.route('/helpdesk_api/helpdesk_api/objects/<model("helpdesk_api.helpdesk_api"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('helpdesk_api.object', {
#             'object': obj
#         })

