{
    "name": "E-learning Invoice",
    "summary": "Generate student invoices linked to CRM leads",
    "version": "1.0",
    "depends": ["account", "crm"],
    'data': [
         'report/report.xml',
         'report/elearning_invoice_template.xml',
         'views/crm_lead_view.xml',
         'views/account_move_view.xml',
    ],

    "installable": True,
    "application": False,
}