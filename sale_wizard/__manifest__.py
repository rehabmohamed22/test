{
    'name': 'Sale Wizard',

    'author': "Rehab Mohamed",

    'category': 'Sales',
    'version': '0.1',
    'depends': ['base' , 'sale'
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_report_wizard_views.xml',
        'reports/sales_report_template.xml',
    ],
    'application': True,
}
