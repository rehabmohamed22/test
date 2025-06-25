# -*- coding: utf-8 -*-
from odoo import models, fields


class PosSession(models.Model):
    _inherit = 'pos.session'

    account_analytic_id = fields.Many2one('account.analytic.account',
        related="config_id.account_analytic_id",
        store=True, string='Analytic Account', copy=False
    )

    def _get_stock_expense_vals(self, exp_account, amount, amount_converted):
        res = super(PosSession, self)._get_stock_expense_vals(exp_account, amount, amount_converted)
        res['analytic_distribution'] = { self.account_analytic_id.id: 100}
        return res

    def _get_stock_output_vals(self, out_account, amount, amount_converted):
        res = super(PosSession, self)._get_stock_output_vals(out_account, amount, amount_converted)
        res['analytic_distribution'] = { self.account_analytic_id.id: 100}
        return res

    def _prepare_line(self, order_line):
        res = super(PosSession, self)._prepare_line(order_line)
        res['analytic_distribution'] = { order_line.order_id.account_analytic_id.id: 100}
        return res

    def _get_sale_vals(self, key, amount, amount_converted):
        res = super(PosSession, self)._get_sale_vals(key, amount, amount_converted)
        res['analytic_distribution'] = { self.account_analytic_id.id: 100}
        return res

    def _get_invoice_receivable_vals(self, amount, amount_converted):
        res = super(PosSession, self)._get_invoice_receivable_vals(amount, amount_converted)
        res['analytic_distribution'] = { self.account_analytic_id.id: 100}
        return res

    def _get_tax_vals(self, key, amount, amount_converted, base_amount_converted):
        res = super(PosSession, self)._get_tax_vals(key, amount, amount_converted, base_amount_converted)
        res['analytic_distribution'] = { self.account_analytic_id.id: 100}
        return res

    def _get_combine_receivable_vals(self, payment_method, amount, amount_converted):
        res = super(PosSession, self)._get_combine_receivable_vals(payment_method, amount, amount_converted)
        res['analytic_distribution'] = { self.account_analytic_id.id: 100}
        return res

    def _get_split_receivable_vals(self, payment, amount, amount_converted):
        res = super(PosSession, self)._get_split_receivable_vals(payment, amount, amount_converted)
        res['analytic_distribution'] = { self.account_analytic_id.id: 100}
        return res

    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        res = super(PosSession, self)._validate_session(balancing_account=balancing_account, amount_to_balance=amount_to_balance, bank_payment_method_diffs=bank_payment_method_diffs)
        all_moves = self._get_related_account_moves()
        lines = all_moves.mapped('line_ids')
        for line in lines:
            if line.account_id.account_type in ['income','income_other','expense','asset_current']:
                line.analytic_distribution = { self.account_analytic_id.id: 100}
            else:
                line.analytic_distribution = False
        return res

class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    def _get_taxes_info(self, taxes):
        print("11111111111111111111111111111111")
        total_tax_amount = 0
        total_base_amount = taxes.get('base_amount', False)
        for tax in taxes.get('taxes', {}).values():
            total_tax_amount += tax.get('tax_amount', 0.0)
        return {
            'tax_amount': total_tax_amount,
            'base_amount': total_base_amount
        }