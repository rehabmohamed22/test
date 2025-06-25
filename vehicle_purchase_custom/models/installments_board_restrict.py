from odoo import models, api
from odoo.exceptions import ValidationError

class InstallmentsBoard(models.Model):
    _inherit = 'installments.board'

    @api.constrains('amount')
    def _check_editable_and_total_validation(self):
        for rec in self:
            if rec.paid_amount > 0 and rec.amount != rec._origin.amount:
                raise ValidationError("You cannot modify this installment amount because it has already been partially or fully paid.")

        if self and self[0].vehicle_purchase_order_id:
            order = self[0].vehicle_purchase_order_id
            all_installments = self.env['installments.board'].search([
                ('vehicle_purchase_order_id', '=', order.id)
            ])
            total = sum(line.amount for line in all_installments)
            expected = order.total_installment_cost

            if abs(total - expected) > 0.01:
                raise ValidationError(
                    f"Total of installments ({total:.2f}) must equal original amount: {expected:.2f}"
                )
