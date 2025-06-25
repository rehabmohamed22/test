from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    img_before = fields.Binary(string="Image Before",attachment=True  )

    img_after = fields.Binary(string="Image After",attachment=True  )


