from odoo import models, fields, api


class LabPatientInvoice(models.Model):
    _name = 'lab.patient.invoice'
    _description = 'Patient Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Invoice Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('lab.patient.invoice'))
    patient_id = fields.Many2one('lab.patient', string='Patient', required=True, tracking=True)
    visit_id = fields.Many2one('lab.patient.visit', string='Visit')
    amount_total = fields.Float(string='Total Amount', compute='_compute_total', store=True, tracking=True)
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid')
    ], string='Payment Status', default='pending', tracking=True)
    payment_date = fields.Date(string='Payment Date')

    invoice_line_ids = fields.One2many('lab.patient.invoice.line', 'invoice_id', string='Invoice Lines')

    @api.depends('invoice_line_ids.price_subtotal')
    def _compute_total(self):
        for invoice in self:
            invoice.amount_total = sum(line.price_subtotal for line in invoice.invoice_line_ids)

    def action_mark_as_paid(self):
        """Marks the invoice as paid and sets the payment date"""
        for invoice in self:
            invoice.payment_status = 'paid'
            invoice.payment_date = fields.Date.today()


class LabPatientInvoiceLine(models.Model):
    _name = 'lab.patient.invoice.line'
    _description = 'Patient Invoice Line'

    invoice_id = fields.Many2one('lab.patient.invoice', string='Invoice', required=True, ondelete='cascade')
    service_id = fields.Many2one('product.product', string='Service', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
