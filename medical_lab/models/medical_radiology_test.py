from odoo import models, fields, api


class MedicalRadiologyTest(models.Model):
    _name = "medical.radiology.test"
    _description = "Radiology Test"

    name = fields.Char(string="Test Name", required=True)
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
    normal_values = fields.Text(string="Normal Values")

    doctor_id = fields.Many2one("res.partner", string="Assigned Doctor", domain=[("is_doctor", "=", True)])
    patient_id = fields.Many2one("res.partner", string="Patient", required=True, domain=[("is_patient", "=", True)])

    result = fields.Text(string="Result")
    test_date = fields.Datetime(string="Test Date", default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="Status", default='draft')

    def action_mark_done(self):
        """Mark the test as Done"""
        self.state = 'done'
