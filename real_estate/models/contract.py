from odoo import models, fields


class Contract(models.Model):
    _name = 'contract'
    _description = 'Real Estate Contract'

    name = fields.Char(string='Contract Name', required=True)
    contract_type = fields.Selection([
        ('sale', 'Sale'),
        ('rental', 'Rental')
    ], string='Contract Type')
    property_id = fields.Many2one('property', string='Property')
    customer_id = fields.Many2one('customer', string='Customer')
    amount = fields.Float(string='Amount')
