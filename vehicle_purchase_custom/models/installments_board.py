from odoo import models, fields

class InstallmentsBoard(models.Model):
    _inherit = 'installments.board'

    order_name = fields.Char(related='vehicle_purchase_order_id.name', string='Order Reference', store=True)
    vendor_id = fields.Many2one(related='vehicle_purchase_order_id.vendor_id', string='Customer', store=True)

    state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('paid', 'Paid'),
            ('partial_paid', 'Partial Paid')
        ],
        string='State',
        compute='_compute_state',
        store=True,
    )
