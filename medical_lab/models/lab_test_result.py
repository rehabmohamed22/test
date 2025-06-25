from odoo import models, fields, api

class LabTestResult(models.Model):
    _name = 'medical.lab.test.result'
    _description = 'Lab Test Result'

    patient_id = fields.Many2one('medical.patient', string="Patient", required=True)
    test_id = fields.Many2one('medical.lab.test', string="Lab Test", required=True)
    result_value = fields.Char(string="Result")
    normal_range = fields.Char(related='test_id.normal_range', string="Normal Range", readonly=True)
    responsible_doctor = fields.Many2one('res.users', string="Responsible Doctor", required=True)
    date_tested = fields.Datetime(string="Date Tested", default=fields.Datetime.now)

    @api.onchange('test_id')
    def _onchange_test_id(self):
        """ تحديث النطاق الطبيعي عند اختيار تحليل """
        if self.test_id:
            self.normal_range = self.test_id.normal_range
