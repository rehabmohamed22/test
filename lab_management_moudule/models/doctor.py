from odoo import models, fields


class LabDoctor(models.Model):
    _name = 'lab.doctor'
    _description = 'Lab Doctor'
    _rec_name = 'name'

    name = fields.Char(string='Doctor Name', required=True)
    specialization = fields.Char(string='Specialization', required=True)
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')

    lab_test_ids = fields.One2many('lab.test', 'doctor_id', string='Lab Tests')
    radiology_ids = fields.One2many('lab.radiology', 'doctor_id', string='Radiology Tests')
