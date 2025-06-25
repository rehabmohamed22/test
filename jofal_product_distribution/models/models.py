from odoo import models, fields, api

class StockScrap(models.Model):
    _inherit = ['stock.scrap', 'analytic.mixin']
    _name = 'stock.scrap'


    def action_open_journal_entry(self):
        self.ensure_one()
        move_obj = self.env['account.move']

        valuation_layer = self.env['stock.valuation.layer'].search([('stock_move_id.scrap_id', '=', self.id)], limit=1)

        if valuation_layer:
            existing_move = move_obj.search([('stock_valuation_layer_ids', 'in', valuation_layer.id)], limit=1)
        else:
            existing_move = False

        if existing_move:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Journal Entry',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': existing_move.id,
                'target': 'current',
            }
        else:
            return {'type': 'ir.actions.act_window_close'}



class StockValuationLayer(models.Model):
    _inherit = ['stock.valuation.layer', 'analytic.mixin']
    _name = 'stock.valuation.layer'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            stock_move = self.env['stock.move'].browse(vals.get('stock_move_id'))
            if stock_move and stock_move.scrap_id:
                scrap = stock_move.scrap_id
                if scrap.analytic_distribution:
                    print(scrap.analytic_distribution)
                    vals['analytic_distribution'] = scrap.analytic_distribution  # تمرير البيانات من Scrap

        return super().create(vals_list)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        res = super()._post(soft)

        for move in self:
            for valuation_layer in move.stock_valuation_layer_ids:
                if valuation_layer.analytic_distribution:
                    for line in move.line_ids:
                        valuation_location = self.env['stock.scrap'].search([
                            ('scrap_location_id.valuation_in_account_id', '=', line.account_id.id)
                        ], limit=1)

                        if valuation_location:
                            line.write({'analytic_distribution': valuation_layer.analytic_distribution})

        return res

