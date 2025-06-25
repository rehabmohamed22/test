{
    'name': 'CRM Student Invoice',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Create invoices for students directly from CRM Leads',
    'depends': ['crm', 'account'],
    'data': [
        'views/crm_invoice_action.xml',
        'report/report.xml',
        'report/report_invoice_student_custom.xml',
    ],

'assets': {
    'web.report_assets_common': [
        'crm_student_invoice/static/src/css/student_invoice.css',
    ],
},

    'installable': True,
    'auto_install': False,
    'application': False,
}
