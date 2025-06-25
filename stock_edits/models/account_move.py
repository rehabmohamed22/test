from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Account Move Inherit"

    partner_ref = fields.Char(
        related="partner_id.ref",
        store=1
    )
