{
    'name': 'SO Payment Type to Invoice',
    'version': '1.0',
    'summary': 'Transfer payment method from Sale Order to Invoice',
    'category': 'Sales',
    'author': 'Rehab Mohamed',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
}
