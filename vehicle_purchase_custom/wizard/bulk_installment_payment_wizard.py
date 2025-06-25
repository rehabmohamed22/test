from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BulkInstallmentPaymentWizard(models.TransientModel):
    _name = 'bulk.installment.payment.wizard'
    _description = 'Bulk Installment Payment Wizard'

    partner_id = fields.Many2one('res.partner', string="Vendor", required=True)
    payment_lines = fields.One2many('bulk.installment.payment.line', 'wizard_id', string="Payment Lines")

    def action_pay(self):
        for line in self.payment_lines:
            po = line.purchase_order_id
            amount_to_pay = line.amount

            if not po or amount_to_pay <= 0:
                continue

            paid = 0
            for installment in po.installment_board_ids.filtered(lambda i: i.state != 'paid'):
                if paid >= amount_to_pay:
                    break
                remaining = installment.remaining_amount
                to_pay = min(remaining, amount_to_pay - paid)
                installment.paid_amount += to_pay
                paid += to_pay
                installment._compute_state()

            self.env['account.payment'].create({
                'partner_id': po.vendor_id.id,
                'amount': amount_to_pay,
                'payment_type': 'outbound',
                'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                'partner_type': 'supplier',
                'date': fields.Date.today(),
                'narration': f"Bulk payment for {po.name}",

            })


class BulkInstallmentPaymentLine(models.TransientModel):
    _name = 'bulk.installment.payment.line'
    _description = 'Bulk Installment Payment Line'

    wizard_id = fields.Many2one('bulk.installment.payment.wizard', required=True, ondelete="cascade")
    purchase_order_id = fields.Many2one('vehicle.purchase.order', string="PO", required=True)
    amount = fields.Float(string="Amount to Pay", required=True)
