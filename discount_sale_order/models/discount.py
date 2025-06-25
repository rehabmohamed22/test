from odoo import models,api,fields

class Discount(models.Model):
    _inherit = 'res.partner'

    discount = fields.Float(string="Discount")
