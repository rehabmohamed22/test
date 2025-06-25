{
    'name': 'Custom Partner Journal',
    'version': '1.0',
    'depends': ['base', 'account','sale','purchase','hr'],
    'category': 'Accounting',
    'description': 'Set default journal per partner and apply it in invoices/bills automatically.',
    'data': [
        'views/partner_journal_view.xml',
        'views/views.xml',
        'views/crm_team.xml',
        'views/account_payment.xml'

    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
