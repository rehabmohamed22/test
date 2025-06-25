from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=False,
        default=False
    )

    def default_get(self, fields):
        res = super().default_get(fields)
        if 'journal_id' in fields:
            res['journal_id'] = False
        return res
