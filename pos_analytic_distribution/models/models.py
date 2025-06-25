# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Default POS Analytic Account',
        config_parameter='point_of_sale.default_pos_analytic_account_id'
    )

class PosSession(models.Model):
    _inherit = 'pos.session'

    def assign_analytic_account_to_moves(self):
        analytic_id = self.env['ir.config_parameter'].sudo().get_param('point_of_sale.default_pos_analytic_account_id')
        print(analytic_id)
        if not analytic_id:
            return

        analytic_id = int(analytic_id)
        for session in self:
            if session.move_id:
                for line in session.move_id.line_ids:
                    if not line.analytic_distribution and line.account_id.account_type in ['income', 'expense'] and line.debit:
                        line.analytic_distribution = {analytic_id: 1.0}
                        entry_amount = self.env['account.move'].search([('ref','=',session.name),('move_type','=','entry')]).mapped('debit')
                        entry_amount_sum = sum(entry_amount)
                        entry_amount_line = self.env['account.analytic.line'].search([
                            ('ref','=',session.name)
                        ])
                        entry_amount_line.amount = entry_amount_sum



    @api.model
    def action_pos_session_close(self, balancing_account=False, amount_to_balance=0.0, bank_payment_method_diffs=None):
        res = super().action_pos_session_close(balancing_account, amount_to_balance, bank_payment_method_diffs)
        self.assign_analytic_account_to_moves()
        return res
