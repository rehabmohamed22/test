{
    'name': 'HR Job Department Restriction',
    'version': '1.0',
    'summary': 'Restrict HR Jobs by Department',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_job_restriction_rules.xml',
        'views/hr_job_views.xml',
        'report/hr_job_department_report.xml',
        'data/hr_job_report_action.xml',
        'wizard/hr_job_restriction_wizard_view.xml',


    ],
    'installable': True,
}
