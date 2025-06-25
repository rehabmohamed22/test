from odoo import models, fields

class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    analytic_distribution = fields.Json(
        string="Analytic Distribution",
        help="Set distribution by analytic account in JSON format"
    )

    analytic_precision = fields.Integer(
        string="Analytic Precision",
        default=2,
        help="Precision for analytic distribution"
    )
    