{
    "name": "Public Holiday Management",
    "version": "1.0",
    "category": "Human Resources",
    "summary": "Manage official public holidays and block leave requests on those days",
    'depends': ['base', 'hr_holidays'],

    "data": [
        'security/ir.model.access.csv',

        # "views/generate_public_holiday_wizard_views.xml",
        "views/public_holiday_views.xml"
    ],
    "installable": True,
    "application": False
}
