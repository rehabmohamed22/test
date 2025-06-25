from odoo import models, fields, api


class Property(models.Model):
    _name = 'property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True)
    property_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('villa', 'Villa'),
        ('apartment', 'Apartment'),
        ('land', 'Land')
    ], string='Property Type')
    status = fields.Selection([
        ('available', 'Available'),
        ('under_construction', 'Under Construction'),
        ('rented', 'Rented'),
        ('sold', 'Sold')
    ], string='Status')
    project_id = fields.Many2one('project', string='Construction Project')
