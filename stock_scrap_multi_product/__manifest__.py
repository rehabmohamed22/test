{
    'name': 'Scrap Multiple Products',
    'version': '1.0',
    'depends': ['base','stock'],
    'category': 'Inventory',
    'summary': 'Allow multiple products in Scrap Order',
    'description': """This module allows adding multiple products to a single scrap order.""",
    'data': [
        'security/ir.model.access.csv',
        'views/stock_scrap_view.xml',
    ],
    'installable': True,
    'application': False,
}
