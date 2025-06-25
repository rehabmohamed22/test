from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_journal_id = fields.Many2one(
        'account.journal',
        string='Default Journal',
        domain="[('type', 'in', ['sale', 'purchase'])]",
        help="Select default journal that will appear in invoices and bills for this partner."
    )

    default_invoice_journal_id = fields.Many2one(
        'account.journal',
        string='Default Sales Journal',
        domain="[('type', '=', 'sale')]",
        help="This journal will be used in Customer Invoices."
    )

    default_bill_journal_id = fields.Many2one(
        'account.journal',
        string='Default Purchase Journal',
        domain="[('type', '=', 'purchase')]",
        help="This journal will be used in Vendor Bills."
    )

