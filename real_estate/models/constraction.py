from odoo import models, fields


class ConstructionProject(models.Model):
    _name = 'project'
    _description = 'Construction Project'

    name = fields.Char(string='Project Name', required=True)
    status = fields.Selection([
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status')
