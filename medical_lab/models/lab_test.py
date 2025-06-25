from odoo import models, fields

class LabTest(models.Model):
    _name = 'medical.lab.test'
    _description = 'Medical Lab Test'

    name = fields.Char(string="Test Name", required=True)
    test_code = fields.Char(string="Test Code")
    normal_range = fields.Char(string="Normal Range")
    price = fields.Float(string="Price")
    doctor_id = fields.Many2one('res.users', string="Responsible Doctor", domain=[('medical_lab_doctor', '=', True)])