from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        # Call the parent method using super()

        for order in self:
            # Confirm and assign linked pickings
            for picking in order.picking_ids:
                if picking.state not in ['done', 'cancel']:
                    picking.action_confirm()  # Confirm picking
                    picking.action_assign()   # Assign products to the picking
                    picking.button_validate()  # Validate the picking

            # Create the invoice if it does not exist
            if not order.invoice_ids:
                order.with_context(default_invoice_origin=order.name).action_create_invoice()

            # Post the invoice if it is in draft state
            for bill in order.invoice_ids.filtered(lambda inv: inv.state == 'draft'):
                bill.invoice_date = date.today()  # Set the invoice date
                bill.action_post()  # Post the invoice

                # Create and post the payment if the invoice is posted
                if bill.state == 'posted':
                    payment_vals = {
                        'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
                        'amount': bill.amount_total,
                        'payment_type': 'outbound',
                        'partner_id': bill.partner_id.id,
                        'partner_type': 'supplier',
                        'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                        # Updated payment method
                        'date': date.today(),
                    }

                    payment = self.env['account.payment'].create(payment_vals)
                    # if payment.state == 'draft':
                    payment.action_post()
        res = super(PurchaseOrder, self).button_confirm()

        return res


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    payment_date = fields.Date(string='Payment Date')
