from odoo import models, fields, api


class LabTestRequest(models.Model):
    _name = 'lab.test.request'
    _description = 'Lab Test Request'
    _order = 'date_requested desc'

    name = fields.Char(string="Request Reference", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: 'New')
    patient_id = fields.Many2one('lab.patient', string="Patient", required=True)
    result_ids = fields.One2many('lab.test.result', 'request_id', string="Test Results")
    doctor_id = fields.Many2one('lab.doctor', string="Referring Doctor")
    test_ids = fields.Many2many('lab.test', string="Requested Tests")
    date_requested = fields.Datetime(string="Request Date", default=fields.Datetime.now, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', required=True)

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lab.test.request') or 'New'
        return super(LabTestRequest, self).create(vals)

    def button_confirm(self):
        self.write({'state': 'confirmed'})

    def button_cancel(self):
        self.write({'state': 'cancelled'})

    def button_done(self):
        self.write({'state': 'done'})

    def button_create_invoice(self):
        """ إنشاء فاتورة للمريض تلقائيًا عند تأكيد الطلب """
        invoice_lines = []
        for test in self.test_ids:
            invoice_lines.append((0, 0, {
                'name': test.name,
                'quantity': 1,
                'price_unit': test.price,
                'account_id': self.env['account.account'].search([], limit=1).id,  # اختيار أي حساب افتراضي
            }))

        invoice = self.env['account.move'].create({
            'partner_id': self.patient_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
        })

        self.write({'invoice_id': invoice.id, 'state': 'invoiced'})
        return {
            'name': "Invoice",
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }
