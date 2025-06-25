from odoo import models, api
from PyPDF2 import PdfMerger
import base64
import io

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _generate_invoice_with_attachments(self):
        """Creates a merged PDF of the invoice and its attachments."""
        self.ensure_one()
        pdf_merger = PdfMerger()

        # Generate invoice PDF
        pdf_content, _ = self.env['ir.actions.report'].sudo()._render_qweb_pdf('account.report_invoice', self.id)
        invoice_pdf = io.BytesIO(pdf_content)
        pdf_merger.append(invoice_pdf)

        # Fetch and merge attachments
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/pdf'),
        ])

        for attachment in attachments:
            if attachment.datas:
                pdf_data = base64.b64decode(attachment.datas)
                pdf_merger.append(io.BytesIO(pdf_data))

        # Create final merged PDF
        merged_pdf = io.BytesIO()
        pdf_merger.write(merged_pdf)
        pdf_merger.close()
        merged_pdf.seek(0)

        return merged_pdf.read()  # Return PDF content

    def action_print_invoice_with_attachments(self):
        """Creates and attaches the merged PDF to the invoice."""
        pdf_data = self._generate_invoice_with_attachments()

        return self.env['ir.attachment'].create({
            'name': f'{self.name}_merged.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_data),
            'res_model': 'account.move',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
