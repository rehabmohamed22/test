from odoo import models, fields

class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    analytic_distribution_ids = fields.One2many(
        'landed.cost.analytic.line',
        'cost_line_id',
        string="Analytic Distribution"
    )
