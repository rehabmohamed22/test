from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # الحقول التعليمية الخاصة بالفاتورة
    student_name = fields.Char(string="Student Name")
    course_name = fields.Char(string="Course Name")
    lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    guardian_email = fields.Char(string="Guardian Email")  # اختياري لو هتستخدمي الإرسال لاحقًا

    def action_print_edu_invoice(self):
        self.ensure_one()
        report = self.env['ir.actions.report']._get_report_from_name('elearning_invoice.report_learning_invoice')
        return report.report_action(self)
