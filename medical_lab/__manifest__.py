{
    'name': 'Medical Lab Management',
    'version': '1.0',
    'summary': 'إدارة التحاليل الطبية والأشعة في Odoo',
    'category': 'Healthcare',
    'author': 'Rahab',
    'website': 'https://yourwebsite.com',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/lab_test_view.xml',  # سنضيفها لاحقًا
        'views/patient_views.xml',
        'views/res_users_view.xml',
        'views/medical_radiology_test_views.xml',
        'views/lab_test_result_views.xml',
        'wizard/lab_selection_wizard.xml',

    ],
    'installable': True,
    'application': True,

}
