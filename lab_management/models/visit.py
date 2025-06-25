import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PatientVisit(models.Model):
    _name = 'lab.patient.visit'
    _description = 'Patient Visit'

    patient_id = fields.Many2one('res.partner', string='Patient', required=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor')
    visit_date = fields.Datetime(string='Visit Date', default=fields.Datetime.now)
    lab_test_ids = fields.Many2many('lab.test.type', string='Lab Tests')
    imaging_test_ids = fields.Many2many('lab.imaging.type', string='Imaging Tests')
    notes = fields.Text(string='Notes')
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    report_url = fields.Char(string='Report URL', compute='_compute_report_url')
    test_result_ids = fields.One2many("lab.test.result", "visit_id", string="Lab Test Results")
    imaging_result_ids = fields.One2many("lab.imaging.result", "visit_id", string="Imaging Results")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('closed', 'Closed'),
    ], default='draft', string='Status')

    def action_create_invoice(self):
        """إنشاء فاتورة وإضافة التحاليل والأشعة المرتبطة تلقائيًا"""
        invoice_lines = []

        for test in self.lab_test_ids:
            if not test.product_id:
                raise UserError(_("Lab test '%s' is not linked to a product!") % test.name)
            invoice_lines.append((0, 0, {
                'product_id': test.product_id.id,
                'name': test.name,
                'quantity': 1,
                'price_unit': test.product_id.list_price,
            }))

        for imaging in self.imaging_test_ids:
            if not imaging.product_id:
                raise UserError(_("Imaging test '%s' is not linked to a product!") % imaging.name)
            invoice_lines.append((0, 0, {
                'product_id': imaging.product_id.id,
                'name': imaging.name,
                'quantity': 1,
                'price_unit': imaging.product_id.list_price,
            }))

        if not invoice_lines:
            raise UserError(_("No tests selected. Please add at least one test to generate an invoice."))

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.patient_id.id,
            'invoice_line_ids': invoice_lines,
        })

        self.invoice_id = invoice.id
        self.state = 'invoiced'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }

    def action_mark_as_paid(self):
        """تمييز الفاتورة كمسددة وإغلاق الزيارة."""
        if not self.invoice_id:
            raise UserError(_("No invoice found!"))

        self.invoice_id.action_post()
        self.invoice_id.payment_state = 'paid'
        self.state = 'paid'

        return {
            'effect': {
                'fadeout': 'slow',
                'message': _("Invoice marked as Paid!"),
                'type': 'rainbow_man',
            }
        }

    def action_close_visit(self):
        """إغلاق الزيارة فقط إذا كانت مدفوعة."""
        if self.state != 'paid':
            raise UserError(_("You cannot close the visit until the invoice is paid."))
        self.state = 'closed'

    def _compute_report_url(self):
        """توليد رابط تحميل التقرير لكل زيارة."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for visit in self:
            visit.report_url = f"{base_url}/report/pdf/lab_management.report_patient_visit_document/{visit.id}"

    def action_generate_report(self):
        """توليد تقرير PDF وإرفاقه في سجل المريض."""
        report = self.env.ref('lab_management.action_patient_visit_report')
        pdf_content, _ = report._render_qweb_pdf([self.id])

        attachment = self.env['ir.attachment'].create({
            'name': f'Patient_Visit_Report_{self.id}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content).decode('utf-8'),
            'res_model': 'lab.patient.visit',
            'res_id': self.id,
        })

        self.message_post(
            body="Patient visit report has been generated.",
            attachment_ids=[attachment.id]
        )

    def action_open_invoice(self):
        """فتح الفاتورة المرتبطة بالزيارة إن وجدت."""
        if not self.invoice_id:
            raise UserError(_("No invoice found!"))

        return {
            'name': _("Invoice"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def action_open_report(self):
        """فتح تقرير الزيارة مباشرة في المتصفح."""
        if not self.report_url:
            raise UserError(_("No report available for this visit."))
        return {
            'type': 'ir.actions.act_url',
            'url': self.report_url,
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        """فتح الـ Wizard تلقائيًا عند إنشاء زيارة جديدة"""
        visit = super(PatientVisit, self).create(vals)
        return visit  # ✅ إعادة الـ visit بدلاً من dict

    def action_open_test_wizard(self):
        """فتح الـ Wizard لاختيار التحاليل أو الأشعة"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Select Test Type',
            'res_model': 'select.lab.type.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_visit_id': self.id}
        }
