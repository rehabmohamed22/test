from odoo import fields,models,api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_account_move(self):
        for rec in self:
            if rec.partner_id.term =='cash':
                rec.journal_id = self.env['account.journal'].search([('code','=','INV1')],limit=1).id
            if rec.partner_id.term == 'credit':
                rec.journal_id = self.env['account.journal'].search([('code', '=', 'INV2')], limit=1).id
