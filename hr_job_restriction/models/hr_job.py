# models/hr_job.py
from odoo import models, fields, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    restricted_department_ids = fields.Many2many(
        'hr.department',
        string='Restricted Departments',
        help='Departments allowed to view/use this job position.'
    )
    category_id = fields.Many2one('hr.job.category', string='Job Category')  # لو مش موجود
    code = fields.Char(string='Job Code')

    # @api.model
    # def read(self, fields=None, load='_classic_read'):
    #     records = super().read(fields=fields, load=load)
    #     for record in records:
    #         if 'category_id' in record and isinstance(record['category_id'], models.BaseModel):
    #             if not record['category_id'].exists():
    #                 record['category_id'] = False
    #     return records
