# -*- coding: utf-8 -*-
# from odoo import http


# class AddAnalyticDistribution(http.Controller):
#     @http.route('/add_analytic_distribution/add_analytic_distribution', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_analytic_distribution/add_analytic_distribution/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_analytic_distribution.listing', {
#             'root': '/add_analytic_distribution/add_analytic_distribution',
#             'objects': http.request.env['add_analytic_distribution.add_analytic_distribution'].search([]),
#         })

#     @http.route('/add_analytic_distribution/add_analytic_distribution/objects/<model("add_analytic_distribution.add_analytic_distribution"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_analytic_distribution.object', {
#             'object': obj
#         })

