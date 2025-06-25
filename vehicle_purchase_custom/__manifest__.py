# -*- coding: utf-8 -*-
{
    'name': "Vehicle Purchase Customization",
    'summary': "Overrides and enhancements to vehicle_purchase module",
    'description': """
This module extends and customizes the vehicle_purchase functionality,
including centralized view of installment boards and reporting.
""",
    'author': "",
    'website': "",
    'category': 'Purchases',
    'version': '17.0.1.0.0',
    'depends': ['base', 'vehicle_purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/installment_board_views.xml',
        'views/import_installments_wizard.xml',
        'views/bulk_installment_payment_wizard.xml',
        'views/vehicle_purchase_order_view_inherit.xml',
    ],
    'installable': True,
    'application': False,
}
