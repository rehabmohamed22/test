from odoo import fields, models


class Customer(models.Model):
    _name = 'customer'
    _description = 'Real Estate Customer'

    name = fields.Char(string='Customer Name', required=True)
    contact = fields.Char(string='Contact')
    email = fields.Char(string='Email')
