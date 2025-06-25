# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    account_analytic_id = fields.Many2one('account.analytic.account',
        related="session_id.account_analytic_id",
        copy=False, store=True, string='Analytic Account')

    @api.model
    def _get_invoice_lines_values(self, line_values, pos_order_line):
        res = super(PosOrder, self)._get_invoice_lines_values(line_values, pos_order_line)
        if pos_order_line.order_id.account_analytic_id.id:
            res['analytic_distribution'] = { pos_order_line.order_id.account_analytic_id.id: 100}
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    account_analytic_id = fields.Many2one('account.analytic.account',
        related="order_id.account_analytic_id", string='Analytic Account')
