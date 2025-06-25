from odoo import models, fields

class Patient(models.Model):
    _name = 'lab.patient'
    _description = 'Patient'

    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age', required=True)
    phone = fields.Char(string='Phone')
    medical_history = fields.Text(string='Medical History')
