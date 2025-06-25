from odoo import models, fields

class LandedCostAnalyticLine(models.Model):
    _name = 'landed.cost.analytic.line'
    _description = 'Landed Cost Analytic Distribution Line'

    cost_line_id = fields.Many2one('stock.landed.cost.lines', required=True, ondelete="cascade", string="Cost Line")
    account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    percentage = fields.Float(string='Percentage', required=True)
