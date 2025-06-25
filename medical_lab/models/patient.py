from odoo import models, fields

class MedicalPatient(models.Model):
    _name = 'medical.patient'
    _description = 'Medical Patient'

    name = fields.Char(string="Patient Name", required=True)
    age = fields.Integer(string="Age")
    phone = fields.Char(string="Phone Number")
    medical_history = fields.Text(string="Medical History")
    lab_test_results = fields.One2many('medical.lab.test.result', 'patient_id', string="Lab Test Results")