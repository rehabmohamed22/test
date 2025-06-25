{
    'name': 'Stock Edits',
    'summary': 'Stock Edits',
    'author': "Amr Othman",
    'company': '',
    'website': "",
    'version': '17.0',
    'category': 'Inventory',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'stock',
        'account',
        'sale',
        'purchase',
        'hr','project_ledger_filter'
    ],
    'data': [
        'security/groups.xml',
        'security/res_partner_rules.xml',
        'data/mail_template_data.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/stock_picking.xml',
        'views/purchase_order.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

