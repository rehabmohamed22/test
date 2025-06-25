# __manifest__.py
{
    'name': 'HR Job Department Restriction',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Restrict HR Jobs visibility per department',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_job_record_rule.xml',
        'views/hr_job_views.xml',
        'views/hr_job_menu.xml',
        'reports/hr_job_report.xml',
        # 'reports/job_department_templates.xml',

    ],
    'installable': True,
    'application': False,
}
