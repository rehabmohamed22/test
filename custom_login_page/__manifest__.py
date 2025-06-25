{
    'name': 'Custom Login Design',
    'version': '1.0',
    'category': 'Tools',
    'author': 'Rehab',
    'website': 'your-website.com',
    'depends': ['web'],
    'data': [
        'views/login_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_login_page/static/src/css/login_style.css',
        ],
    },

    'installable': True,
    'auto_install': False,
}
