from odoo import models, fields, api

class LabPatient(models.Model):
    _name = 'lab.patient'
    _description = 'Lab Patient'
    _rec_name = 'name'

    name = fields.Char(string='Patient Name', required=True)
    age = fields.Integer(string='Age', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True)
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    medical_history = fields.Text(string='Medical History')

    lab_test_ids = fields.One2many('lab.test', 'patient_id', string='Lab Tests')
    radiology_ids = fields.One2many('lab.radiology', 'patient_id', string='Radiology Tests')
