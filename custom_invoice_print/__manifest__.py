{
    'name': 'Custom Invoice Print with Attachments',
    'version': '1.0',
    'summary': 'Print invoice along with its attachments in a single PDF file.',
    'category': 'Accounting',
    'author': 'Rahab',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
