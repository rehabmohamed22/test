from odoo import models, fields


class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    analytic_distribution = fields.Json(
        string='Analytic Distribution',
    )
