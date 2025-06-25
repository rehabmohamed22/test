from odoo import fields,models,api

class WebsiteProduct(models.Model):
     _inherit = 'product.template'

     ticket_limit = fields.Boolean(string="Ticket Limit")
     min = fields.Integer(string="Min")
     max = fields.Integer(string="Max")


