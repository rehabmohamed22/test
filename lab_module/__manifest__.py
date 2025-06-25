{
    'name': 'Lab Module',
    'version': '1.0',
    'summary': 'A module to manage medical lab tests and radiology services.',
    'description': """
        This module helps in managing a medical lab including 
        patients, doctors, tests, invoices, and results.
    """,
    'category': 'Healthcare',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/lab_test_sequence.xml',
        'data/lab_test_result_sequence.xml',
        'reports/test_request_report.xml',  # ملف التقرير هنا قبل النماذج
        'views/patient_views.xml',
        'views/doctor_views.xml',
        'views/test_views.xml',
        'views/test_request_views.xml',
        'views/test_result_views.xml',
        'views/radiology_request_views.xml',
        'views/menu.xml',
        'wizard/lab_test_wizard_view.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
