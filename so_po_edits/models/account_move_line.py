from odoo import _, api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _description = "Account Move Line Inherit"

    index = fields.Integer()
