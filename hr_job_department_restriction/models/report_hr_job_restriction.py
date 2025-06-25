from odoo import models

class ReportHRJobRestriction(models.AbstractModel):
    _name = 'report.hr_job_department_restriction.report_hr_job_restriction'
    _description = 'HR Job Restriction Report'

    def _get_filtered_jobs(self, department_id, category_id):
        domain = []
        if department_id:
            domain.append(('restricted_department_ids', 'in', department_id))
        if category_id:
            domain.append(('category_id', '=', category_id))
        return self.env['hr.job'].search(domain)

    def _get_report_values(self, docids, data=None):
        jobs = self._get_filtered_jobs(data.get('department_id'), data.get('category_id'))
        return {
            'doc_ids': jobs.ids,
            'doc_model': 'hr.job',
            'docs': jobs,
        }
