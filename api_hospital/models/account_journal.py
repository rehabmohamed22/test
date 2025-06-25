from odoo import fields,models,api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_type = fields.Selection(string="Payment Type", selection=[('cash', 'Cash'), ('check', 'Check'),('visa','Visa') ] )
