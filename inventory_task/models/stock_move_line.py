from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    picking_date = fields.Date(related='picking_id.date', string="Picking Date", store=True)
