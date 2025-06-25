# -*- coding: utf-8 -*-
# from odoo import http


# class ZidConnector(http.Controller):
#     @http.route('/zid_connector/zid_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zid_connector/zid_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('zid_connector.listing', {
#             'root': '/zid_connector/zid_connector',
#             'objects': http.request.env['zid_connector.zid_connector'].search([]),
#         })

#     @http.route('/zid_connector/zid_connector/objects/<model("zid_connector.zid_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zid_connector.object', {
#             'object': obj
#         })

