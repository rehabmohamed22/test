from odoo import models, fields

class LabTestResult(models.Model):
    _name = 'lab.test.result'
    _description = 'Lab Test Result'

    visit_id = fields.Many2one('lab.patient.visit', string='Patient Visit', ondelete='cascade', required=True)
    lab_test_type_id = fields.Many2one('lab.test.type', string='Lab Test', required=True)
    result = fields.Char(string='Result', required=True)
    notes = fields.Text(string='Notes')
    test_id = fields.Many2one("lab.test.type", string="Test Name", required=True)
    result_value = fields.Char(string="Result", required=True)
    normal_range = fields.Char(string="Normal Range")