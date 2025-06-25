# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    partner_id = fields.Many2one('res.partner', string="Customer")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    analytic_distribution = fields.Many2many(
        'account.analytic.account',
        string="Analytics Distribution"
    )
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
        domain="[('id', 'in', analytic_account_ids)]"
    )

    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string="Available Analytic Accounts",
        compute="_compute_analytic_accounts",
        store=True
    )

    @api.depends('partner_id')
    def _compute_analytic_accounts(self):
        for record in self:
            if record.partner_id:
                # ✅ Now it gets only the accounts selected in `analytic_distribution` from `res.partner`
                record.analytic_account_ids = record.partner_id.analytic_distribution
            else:
                record.analytic_account_ids = self.env['account.analytic.account'].browse([])  # Ensure empty recordset


from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('order_id')
    def _onchange_order_id(self):
        """Automatically assign `analytic_distribution` based on `analytic_account_id` from `sale.order`."""
        if self.order_id and self.order_id.analytic_account_id:
            self.analytic_distribution = {self.order_id.analytic_account_id.id: 100.0}  # Assign full value to selected analytic account


    def _prepare_invoice_line(self, **optional_values):
        """Ensure `analytic_distribution` is passed to the invoice correctly."""
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.analytic_distribution:
            res['analytic_distribution'] = self.analytic_distribution
        return res