from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    salesperson_user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        domain=[],
        help='Internal or Portal user assigned as Salesperson.'
    )
