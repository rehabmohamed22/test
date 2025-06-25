# -*- coding: utf-8 -*-
{
    'name': "zid_connector",

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
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'website_appointment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/zid_order_sync_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/ir_cron.xml',
        'views/zid_order_views.xml',
        'views/zid_settings_views.xml',
        'views/zid_customer.xml',
        'views/zid_customer_fetch.xml',
        'views/zid_order_view_get.xml',
        'views/zid_product.xml',
        'views/sale_order.xml',
        'views/product_product.xml',
        'data/scheduled_actions.xml',
        'data/system_paameters.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
