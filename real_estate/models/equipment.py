from odoo import models, fields


class Equipment(models.Model):
    _name = 'equipment'
    _description = 'Construction Equipment'

    name = fields.Char(string='Equipment Name', required=True)
    project_id = fields.Many2one('project', string='Assigned Project')
    maintenance_schedule = fields.Date(string='Next Maintenance')
