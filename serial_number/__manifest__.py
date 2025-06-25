{
    'name': "Serial Number for Lines",

    'author': "Rehab Mohamed",

    'category': 'Train',
    'version': '0.1',
    'depends': ['sale', 'purchase', 'stock', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_serial_number_views.xml',
        'views/purchase_serial_number_views.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_serial_number_views.xml',
        'views/invoice_serial_number_views.xml',
        'views/account_move_view.xml',
        'reports/sale_serial_number_report.xml',
        'reports/sale_order_report.xml',

    ],
    'application': True,
}

