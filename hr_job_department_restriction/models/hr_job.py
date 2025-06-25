from odoo import models, fields, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    job_code = fields.Char(string='Job Code')
    restricted_department_ids = fields.Many2many(
        'hr.department',
        string='Restricted Departments',
        help='Departments allowed to access this job. Empty means accessible to all.'
    )
    category_id = fields.Many2one(
        'hr.job.category',
        string='Category'
    )
    _sql_constraints = [
        ('restricted_department_ids_index', 'INDEX(restricted_department_ids)', 'Index for restricted departments'),
    ]

    # @api.model
    # def create(self, vals):
    #     if not vals.get('category_id'):
    #         default_category = self.env['hr.job.category'].search([], limit=1)
    #         if default_category:
    #             vals['category_id'] = default_category.id
    #     return super().create(vals)
