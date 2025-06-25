from odoo import models, fields

class LabPatient(models.Model):
    _name = 'lab.patient'
    _description = 'Lab Patient'
    _rec_name = 'name'  # تحديد اسم العرض في Odoo

    name = fields.Char(string="Patient Name", required=True)
    age = fields.Integer(string="Age", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender", required=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Text(string="Address")
    medical_history = fields.Text(string="Medical History")
