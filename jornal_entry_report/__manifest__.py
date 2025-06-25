{
    'name': "Journal Entry",

    'author': "Rehab Mohamed",

    'category': 'Train',
    'version': '0.1',
    'depends': ['base' , 'account'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_wizard_views.xml',
        'reports/sales_report_template.xml'
    ],
    'application': True,
}

