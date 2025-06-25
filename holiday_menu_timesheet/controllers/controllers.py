# -*- coding: utf-8 -*-
# from odoo import http


# class HolidayMenuTimesheet(http.Controller):
#     @http.route('/holiday_menu_timesheet/holiday_menu_timesheet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/holiday_menu_timesheet/holiday_menu_timesheet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('holiday_menu_timesheet.listing', {
#             'root': '/holiday_menu_timesheet/holiday_menu_timesheet',
#             'objects': http.request.env['holiday_menu_timesheet.holiday_menu_timesheet'].search([]),
#         })

#     @http.route('/holiday_menu_timesheet/holiday_menu_timesheet/objects/<model("holiday_menu_timesheet.holiday_menu_timesheet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('holiday_menu_timesheet.object', {
#             'object': obj
#         })

