from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    zid_customer_id = fields.Integer(string="Zid Customer ID", index=True)
