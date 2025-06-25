# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryTask(http.Controller):
#     @http.route('/inventory_task/inventory_task', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_task/inventory_task/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_task.listing', {
#             'root': '/inventory_task/inventory_task',
#             'objects': http.request.env['inventory_task.inventory_task'].search([]),
#         })

#     @http.route('/inventory_task/inventory_task/objects/<model("inventory_task.inventory_task"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_task.object', {
#             'object': obj
#         })

