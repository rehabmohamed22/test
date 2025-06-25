# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class discount_sale_order(models.Model):
#     _name = 'discount_sale_order.discount_sale_order'
#     _description = 'discount_sale_order.discount_sale_order'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

