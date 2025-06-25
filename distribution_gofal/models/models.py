#-*- coding: utf-8 -*-

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = "stock.location"

    analytic_distribution = fields.Json(string="Analytics Distribution")






