from odoo import fields, models


class Unit(models.Model):
    _name = 'unit'
    _description = 'Real Estate Unit'

    name = fields.Char(string='Unit Name', required=True)
    property_id = fields.Many2one('property', string='Property')
    status = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('sold', 'Sold')
    ], string='Status')