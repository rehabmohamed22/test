from odoo import models, fields

class HRJobRestrictionWizard(models.TransientModel):
    _name = 'hr.job.restriction.wizard'
    _description = 'Job Restriction Filter Wizard'

    department_id = fields.Many2one('hr.department', string='Department')
    category_id = fields.Many2one('hr.job.category', string='Category')

    def print_report(self):
        data = {
            'department_id': self.department_id.id if self.department_id else False,
            'category_id': self.category_id.id if self.category_id else False,
        }
        return self.env.ref('hr_job_department_restriction.action_hr_job_restriction_report').report_action(self, data=data)
