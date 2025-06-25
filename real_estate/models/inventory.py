from odoo import fields, models


class Inventory(models.Model):
    _name = 'inventory'
    _description = 'Construction Inventory'

    name = fields.Char(string='Material Name', required=True)
    quantity = fields.Integer(string='Quantity')
    project_id = fields.Many2one('project', string='Used In Project')
