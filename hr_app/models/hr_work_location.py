from odoo import fields, models

class HrWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    latitude = fields.Float(string='Latitude')
    longitude = fields.Float(string='Longitude')
