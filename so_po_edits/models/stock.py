from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
class PopupMessage(models.TransientModel):
    _name = 'popup.message'
    _description = 'Popup Message Confirmation'

    title = fields.Char(string="Title", required=True)
    message = fields.Text(string="Message", required=True)
    confirm_button_text = fields.Char(string="Confirm Button Text", default="Confirm")
    cancel_button_text = fields.Char(string="Cancel Button Text", default="Cancel")

    def action_confirm(self):
        """ User pressed 'Continue', validate the picking and refresh the view """
        picking_id = self.env.context.get('default_picking_id')

        if picking_id:
            picking = self.env['stock.picking'].browse(picking_id)

            if picking.exists():
                print(f"BEFORE Validation: Picking ID {picking_id}, State: {picking.state}")

                picking.with_context(skip_popup=True).button_validate()

                print(f"AFTER Validation: Picking ID {picking_id}, State: {picking.state}")

                picking._flush()
                picking._invalidate_cache()

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.picking',
                    'view_mode': 'form',
                    'res_id': picking_id,
                    'target': 'current',
                    'flags': {'reload': True},
                }

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """ Close the popup if user clicks Cancel """
        return {'type': 'ir.actions.act_window_close'}


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """ Override button_validate to show a popup when required """

        if self.env.context.get('skip_popup'):
            return super(StockPicking, self).button_validate()

        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                for move in rec.move_ids_without_package:
                    orderpoint = self.env['stock.warehouse.orderpoint'].search(
                        [('product_id', '=', move.product_id.id)], limit=1
                    )
                    if orderpoint and ( move.product_id.qty_available - move.product_uom_qty) < orderpoint.product_min_qty or (move.product_id.qty_available - move.quantity) < orderpoint.product_min_qty :
                        popup = self.env['popup.message'].create({
                            'title': 'Warning',
                            'message': 'Are you sure you want to proceed with validation?',
                            'confirm_button_text': 'Continue',
                            'cancel_button_text': 'Cancel',
                        })

                        return {
                            'name': _('Warning'),
                            'type': 'ir.actions.act_window',
                            'res_model': 'popup.message',
                            'view_mode': 'form',
                            'res_id': popup.id,
                            'view_id': self.env.ref('so_po_edits.popup_message_form_view').id,
                            'target': 'new',
                            'context': {
                                'default_picking_id': rec.id,
                            }
                        }

            for move in rec.move_ids_without_package:
                delivered_qty = sum(
                    self.env['stock.move'].search([
                        ('type', '=', 'outgoing'),
                        ('product_id', '=', move.product_id.id),
                        ('partner_id', '=', rec.partner_id.id),
                        ('state', '=', 'done')
                    ]).mapped('product_uom_qty')
                    )
                print(delivered_qty)
                if rec.return_id and rec.picking_type_code =="incoming":
                    if move.product_uom_qty > delivered_qty or move.quantity > delivered_qty:
                        raise ValidationError(_(f"You cannot return more quantities than were delivered for the product {move.product_id.display_name}"))

        # ✅ If no popup is needed, proceed with normal validation
        return super(StockPicking, self).button_validate()

    is_indexed = fields.Integer()


    type = fields.Selection(related='picking_type_id.code', store=True)
    product_ids = fields.Many2many('product.product', compute='set_compute_field')

    @api.depends('partner_id')
    def set_compute_field(self):
        if self.return_id:
            customer_picking_products = self.env['stock.picking'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'done'),
                ('type', '=', 'outgoing'),
            ])
            products = []
            for product in customer_picking_products:
                for move in product.move_ids_without_package:
                    products.append(move.product_id.id)
            self.product_ids = [(6, 0, products)]
        else:
            self.product_ids = self.env['product.product'].search([])
    @api.depends('move_ids_without_package')
    def _compute_line_index(self):
        for rec in self:
            for idx, line in enumerate(rec.move_ids_without_package, start=1):
                line.index = idx

    def add_index_action(self):
        for rec in self:
            if not rec.is_indexed:
                for idx, line in enumerate(rec.move_ids_without_package):
                    line.index = idx + 1
            rec.is_indexed = True


class StockMove(models.Model):
    _inherit = 'stock.move'

    type = fields.Selection(related='picking_id.picking_type_id.code',store = True)
    partner_id = fields.Many2one('res.partner',reltated='picking_id.partner_id',store = True)
    index = fields.Integer(compute='_compute_index', store=True)

    @api.depends('picking_id.move_ids_without_package')
    def _compute_index(self):
        for record in self:
            if record.picking_id:
                for idx, move in enumerate(record.picking_id.move_ids_without_package, start=1):
                    if move == record:
                        record.index = idx
