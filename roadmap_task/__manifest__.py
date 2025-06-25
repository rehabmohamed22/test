{
    'name': "Courses",

    'author': "Rehab Mohamed",

    'category': 'Train',
    'version': '0.1',
    'depends': ['base' , 'sale_management' , 'account_accountant'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/courses_view.xml',
        'views/progress_view.xml',
        'views/evaluation_view.xml',
        'reports/progress_report.xml'
    ],
    'application': True,
}

