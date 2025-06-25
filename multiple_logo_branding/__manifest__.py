# -*- coding: utf-8 -*-
{
    'name': "Multiple Logo Branding",
    'version': '17.0.1.0.0',
    'summary': "logo, branding",
    'author': 'Instantė, UAB',
    'website': 'www.instante.lt',
	'category': 'Sales Management',
    'license': 'AGPL-3',
    'depends': [
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_branding_views.xml',
        'views/res_partner_views.xml',
        'views/report_templates.xml',
    ],
    'images': ['static/description/Cover_image.png'],
    'price': '9.99',
    'currency': 'EUR',
}
