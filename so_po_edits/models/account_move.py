from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Account Move Inherit"

    is_indexed = fields.Boolean()

    @api.constrains('invoice_line_ids')
    @api.onchange('invoice_line_ids')
    def _check_invoice_line_ids(self):
        for idx, line in enumerate(self.invoice_line_ids):
            line.index = idx + 1

    def add_index_action(self):
        for rec in self:
            if not rec.is_indexed:
                for idx, line in enumerate(rec.invoice_line_ids):
                    line.index = idx + 1
            rec.is_indexed = True
