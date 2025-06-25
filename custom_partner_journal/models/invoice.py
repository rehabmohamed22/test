from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id', 'move_type')
    def _onchange_partner_and_type_set_journal(self):
        if self.move_type == 'out_invoice':  # Customer Invoice
            if self.partner_id.default_invoice_journal_id:
                self.journal_id = self.partner_id.default_invoice_journal_id
        elif self.move_type == 'in_invoice':  # Vendor Bill
            if self.partner_id.default_bill_journal_id:
                self.journal_id = self.partner_id.default_bill_journal_id
