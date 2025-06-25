from odoo import models

class ReportHrJobRestriction(models.AbstractModel):
    _name = 'report.hr_job_restriction.report_hr_job_restriction'

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.job'].search([])
        safe_docs = docs.filtered(
            lambda job: all(dep.exists() for dep in job.restricted_department_ids)
        )
        return {'docs': safe_docs}
