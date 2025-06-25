from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        domain=[],  # Remove any domain to show all users
        help='The internal user in charge of communicating with this contact if any.'
    )
