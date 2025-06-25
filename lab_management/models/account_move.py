from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_mark_as_paid(self):
        """تمييز الفاتورة كمدفوعة"""
        self.ensure_one()
        self.payment_state = 'paid'

        # تحديث حالة الزيارة إذا كانت هذه الفاتورة مرتبطة بزيارة مريض
        visit = self.env['lab.patient.visit'].search([('invoice_id', '=', self.id)], limit=1)
        if visit:
            visit.state = 'closed'
