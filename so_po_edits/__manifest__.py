{
    'name': 'SO PO Edits',
    'summary': 'SO PO Edits',
    'author': "Amr Othman",
    'company': '',
    'website': "",
    'version': '17.0',
    'category': 'Purchase',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'account',
        'sale',
        'purchase',
        'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/stock.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

