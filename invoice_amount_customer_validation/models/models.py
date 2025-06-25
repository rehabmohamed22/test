# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'ResPartner'

    total_invoice_amount = fields.Float(string="Amount")
    @api.constrains('total_invoice_amount')
    def _check_total_invoice_amount(self):
        for record in self:
            if record.total_invoice_amount < 0:
                raise ValidationError(_('Amount should be positive.'))

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        result = super(AccountMove, self).action_post()
        customer_total_orders = self.env['sale.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'sale'),
        ])
        total_order_amount = 0
        if customer_total_orders:
            total_order_amount = sum(customer_total_orders.mapped('amount_total'))
        partner_total_due = self.partner_id.total_due
        partner_limit = self.partner_id.total_invoice_amount
        if (partner_total_due + total_order_amount) > partner_limit and partner_limit != 0:
            raise ValidationError(_(f"Customer invoice should be less than {partner_limit}"))
        return result
        # customer_invoice = self.search([
        #     ('partner_id', '=', self.partner_id.id),
        #     ('state', '=', 'posted'),
        #     ('move_type', '=', 'out_invoice'),
        # ])
            #     partner_amount     =


# class AccountPayment(models.Model):
#     _inherit = 'account.payment'
#
#     def action_post(self):
#         result = super(AccountPayment, self).action_post()
#         partner_total_due = self.partner_id.total_due
#         print(partner_total_due)
#         partner_limit = self.partner_id.total_invoice_amount
#         if partner_total_due > partner_limit and partner_limit != 0:
#             raise ValidationError(_(f"Customer invoice should be less than {partner_limit}"))
#         return result


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        customer_total_orders = self.search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'sale'),
        ])

        if customer_total_orders:
            total_amount = sum(customer_total_orders.mapped('amount_total'))

        partner_total_due = self.partner_id.total_due
        total_orders = total_amount
        partner_limit = self.partner_id.total_invoice_amount
        if (partner_total_due + total_orders) > partner_limit and partner_limit != 0:
            raise ValidationError(_(f"Customer Orders should be less than {partner_limit}"))
        return result