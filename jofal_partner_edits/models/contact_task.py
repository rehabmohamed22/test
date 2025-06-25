from odoo import fields, models

class ContactTask(models.Model):
    _inherit = 'res.partner'

    term = fields.Selection([
        ('cash', 'cash'),
        ('credit', 'credit')
    ], string="Payment Method")

    user_id = fields.Many2one(
        'hr.employee', string='Salesperson',
        readonly=False,
        help='The internal user in charge of this contact.')