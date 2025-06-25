from odoo import models, fields

class LabDoctor(models.Model):
    _name = 'lab.doctor'
    _description = 'Lab Doctor'
    _rec_name = 'name'

    name = fields.Char(string="Doctor Name", required=True)
    specialization = fields.Char(string="Specialization")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    hospital = fields.Char(string="Hospital/Clinic")
