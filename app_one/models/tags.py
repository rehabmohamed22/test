from odoo import models , fields

class Tags(models.Model):
    _name = 'tags'

    name = fields.Char(required=True)
