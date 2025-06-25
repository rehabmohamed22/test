{
    'name': 'Sale Order Payment Activity',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Automatically schedule activity based on payment terms',
    'depends': ['sale_management'],
    'data': [
        'views/replenishment_notify_views.xml',
        'data/cron.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
