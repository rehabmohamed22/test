from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_method = fields.Char(string="Payment Method" )
