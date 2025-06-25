{
    'name': 'E-Learning Bsma',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Adds custom fields to CRM and Contacts',
    'depends': ['base', 'crm', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/crm_lead_view.xml',
    ],
    'installable': True,
    'application': False,
}

