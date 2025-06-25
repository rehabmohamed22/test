# -*- coding: utf-8 -*-
# from odoo import http


# class AnalyticDistributionManagement(http.Controller):
#     @http.route('/analytic_distribution_management/analytic_distribution_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/analytic_distribution_management/analytic_distribution_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('analytic_distribution_management.listing', {
#             'root': '/analytic_distribution_management/analytic_distribution_management',
#             'objects': http.request.env['analytic_distribution_management.analytic_distribution_management'].search([]),
#         })

#     @http.route('/analytic_distribution_management/analytic_distribution_management/objects/<model("analytic_distribution_management.analytic_distribution_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('analytic_distribution_management.object', {
#             'object': obj
#         })

