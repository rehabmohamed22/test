from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPMove(models.Model):
    _inherit = "stock.move"
    _description = "Stock Move Inherit"

    on_hand_quantity = fields.Float(
        readonly=1
    )

    index = fields.Integer(compute='_compute_index', store=True)

    @api.depends('picking_id.move_ids_without_package')
    def _compute_index(self):
        for record in self:
            if record.picking_id:
                for idx, move in enumerate(record.picking_id.move_ids_without_package, start=1):
                    if move == record:
                        record.index = idx
    @api.onchange('product_id')
    def check_on_hand_quantity(self):
        for rec in self:
            if rec.picking_code in ['outgoing', 'internal']:
                rec.on_hand_quantity = rec.check_product_on_hand()

    def check_product_on_hand(self):
        onhand = self.env['stock.quant'].sudo().search([
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.picking_id.location_id.id)
        ], limit=1)
        if onhand:
            return onhand.inventory_quantity_auto_apply
        else:
            return 0
