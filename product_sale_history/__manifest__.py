{
    'name': 'Sale Order Wizard',
    'version': '1.0',
    'depends': ['sale'],
    'category': 'Sales',
    'description': "Add wizard button to Sale Order Line",
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_details_wizard.xml',
        'views/sale_order_view.xml',

    ],
    'installable': True,
    'application': False,
}