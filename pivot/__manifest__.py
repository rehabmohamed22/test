# -*- coding: utf-8 -*-
{
    'name': "Pivot sale order",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale_management',
                'rental_edits',
                'sale_renting'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
        'views/wizard_detail_view.xml',
        'views/rental_product.xml',
        'views/sale_order_view.xml',
        'views/wizard_view_product.xml',
        'views/partner.xml',
        'report/rental.xml',
        'report/rental_action.xml',
        'report/report.xml',
        'report/detail_rental.xml',
        'report/product_template_report.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

