from odoo import models, fields

class LabTest(models.Model):
    _name = 'lab.test'
    _description = 'Lab Test'
    _rec_name = 'name'

    name = fields.Char(string="Test Name", required=True)
    test_type = fields.Selection([
        ('analysis', 'Analysis'),
        ('radiology', 'Radiology')
    ], string="Test Type", required=True)
    normal_range = fields.Char(string="Normal Range", help="Only for analysis tests")
    price = fields.Float(string="Price", required=True)
