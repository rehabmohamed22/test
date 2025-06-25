{
    "name": "Landed Cost Analytic Extension (Fixed)",
    "version": "1.0",
    "depends": [
    "stock_landed_costs",
    "account_analytic_distribution"
],

    "author": "Custom",
    "category": "Inventory",
    "description": "Add analytic distribution to landed cost lines",
    "data": [
        'security/ir.model.access.csv',
        "views/inherit_landed_cost_line.xml"
    ],
    "installable": True,
    "application": False
}
