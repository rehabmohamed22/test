{
    'name': "App One",

    'author': "Rehab Mohamed",

    'category': 'Train',
    'version': '0.1',
    'depends': ['base' , 'sale' , 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/property_view.xml',
        'views/owner_view.xml',
        'views/tags_view.xml',
        'views/sale_order_view.xml',
        'views/building_view.xml',
        'reports/owner_property_report.xml',
        'views/property_history_view.xml',
        # 'views/purchase_order_view.xml',
        'wizard/change_state_wizard_view.xml'

    ],
    'assets' : {
        'web.assets_backend' : ['app_one/static/src/css/property.css']
    },
    'application': True,
}

