from odoo import models, fields


class HR(models.Model):
    _name = 'hr'
    _description = 'Construction HR'

    name = fields.Char(string='Employee Name', required=True)
    job_position = fields.Char(string='Job Position')
    salary = fields.Float(string='Salary')
