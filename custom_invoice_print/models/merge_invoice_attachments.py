
from odoo import models

class MergeInvoiceAttachments(models.AbstractModel):
    _name = 'report.merge.invoice.attachments'
    _description = 'Merge Invoice and Attachments into a Single PDF'

    def generate_pdf(self, invoice):
        pdf_data = invoice._generate_invoice_with_attachments()

        return self.env.ref('account.account_invoices').report_action(invoice)
