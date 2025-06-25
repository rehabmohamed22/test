# -*- coding: utf-8 -*-
# from odoo import http


# class ContactTask(http.Controller):
#     @http.route('/contact_task/contact_task', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_task/contact_task/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_task.listing', {
#             'root': '/contact_task/contact_task',
#             'objects': http.request.env['contact_task.contact_task'].search([]),
#         })

#     @http.route('/contact_task/contact_task/objects/<model("contact_task.contact_task"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_task.object', {
#             'object': obj
#         })

