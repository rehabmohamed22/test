from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    sequence = fields.Integer(string="Serial", compute="_compute_sequence", store=True, readonly=True)

    @api.depends('picking_id.move_ids')
    def _compute_sequence(self):
        for picking in self.mapped('picking_id'):
            moves = picking.move_ids.sorted(key=lambda x: x.create_date or (x.id if isinstance(x.id, int) else 0))
            for index, move in enumerate(moves, start=1):
                move.sequence = index