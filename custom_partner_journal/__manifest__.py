{
    'name': 'Custom Partner Journal',
    'version': '1.0',
    'depends': ['base', 'account'],
    'category': 'Accounting',
    'description': 'Set default journal per partner and apply it in invoices/bills automatically.',
    'data': [
        'views/partner_journal_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
