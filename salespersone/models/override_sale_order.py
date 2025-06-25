from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        domain=[],
        help='Internal or portal user assigned to this sales order.'
    )
