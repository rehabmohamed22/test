from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sequence = fields.Integer(string="Serial", compute="_compute_sequence", store=True, readonly=True)

    @api.depends('move_id.invoice_line_ids')
    def _compute_sequence(self):
        for move in self.mapped('move_id'):
            lines = move.invoice_line_ids.sorted(key=lambda x: x.create_date or (x.id if isinstance(x.id, int) else 1))
            for index, line in enumerate(lines, start=1):
                line.sequence = index