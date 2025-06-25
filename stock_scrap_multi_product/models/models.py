# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class stock_scrap_multi_product(models.Model):
#     _name = 'stock_scrap_multi_product.stock_scrap_multi_product'
#     _description = 'stock_scrap_multi_product.stock_scrap_multi_product'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

