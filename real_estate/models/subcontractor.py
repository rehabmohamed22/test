from odoo import fields, models


class Subcontractor(models.Model):
    _name = 'subcontractor'
    _description = 'Construction Subcontractor'

    name = fields.Char(string='Subcontractor Name', required=True)
    service = fields.Char(string='Service')
