from odoo import models, fields, api


class LabTest(models.Model):
    _name = 'lab.test'
    _description = 'Medical Lab Test'
    _rec_name = 'test_name'

    test_name = fields.Char(string='Test Name', required=True)
    test_code = fields.Char(string='Test Code', required=True)
    normal_range = fields.Char(string='Normal Range')  # القيم الطبيعية للتحليل
    unit = fields.Char(string='Unit')  # وحدة القياس (مثل mg/dL)

    patient_id = fields.Many2one('lab.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('lab.doctor', string='Doctor', required=True)

    test_result = fields.Char(string='Test Result')
    result_status = fields.Selection([
        ('pending', 'Pending'),
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal')
    ], string='Result Status', default='pending')

    date_requested = fields.Date(string='Date Requested', default=fields.Date.context_today)
    date_completed = fields.Date(string='Date Completed')

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    @api.onchange('test_result')
    def _check_result_status(self):
        """ تحديث حالة النتيجة بناءً على القيمة المدخلة """
        if self.test_result:
            self.result_status = 'normal' if self.test_result in self.normal_range else 'abnormal'
        else:
            self.result_status = 'pending'
