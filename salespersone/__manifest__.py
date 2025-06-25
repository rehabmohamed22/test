{
    'name': 'Allow Portal Users as Salesperson',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Allow Portal Users to appear as Salesperson',
    'description': 'This module allows portal users to appear in the Salesperson field in Customers and Quotations.',
    'author': '',
    'depends': ['base', 'sales'],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_user_salesperson_rules.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}
