from odoo import models, fields, api


class Accounting(models.Model):
    _name = 'accounting'
    _description = 'Construction Accounting'

    project_id = fields.Many2one('project', string='Project')
    cost = fields.Float(string='Total Cost')
    revenue = fields.Float(string='Total Revenue')
    profit = fields.Float(string='Profit', compute='_compute_profit')

    @api.depends('cost', 'revenue')
    def _compute_profit(self):
        for record in self:
            record.profit = record.revenue - record.cost