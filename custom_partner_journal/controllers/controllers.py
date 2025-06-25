# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPartnerJournal(http.Controller):
#     @http.route('/custom_partner_journal/custom_partner_journal', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_partner_journal/custom_partner_journal/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_partner_journal.listing', {
#             'root': '/custom_partner_journal/custom_partner_journal',
#             'objects': http.request.env['custom_partner_journal.custom_partner_journal'].search([]),
#         })

#     @http.route('/custom_partner_journal/custom_partner_journal/objects/<model("custom_partner_journal.custom_partner_journal"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_partner_journal.object', {
#             'object': obj
#         })

