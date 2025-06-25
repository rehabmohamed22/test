from odoo import models, fields, api

class LabInvoice(models.Model):
    _inherit = 'account.move'

    patient_id = fields.Many2one('lab.patient', string='Patient', required=True)
    lab_test_ids = fields.Many2many('lab.test', string='Lab Tests')
    radiology_ids = fields.Many2many('lab.radiology', string='Radiology Tests')

    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.depends('lab_test_ids', 'radiology_ids')
    def _compute_total(self):
        """ حساب إجمالي الفاتورة بناءً على التحاليل والأشعة المختارة """
        for record in self:
            total = sum(test.invoice_id.amount_total for test in record.lab_test_ids if test.invoice_id) + \
                    sum(radiology.invoice_id.amount_total for radiology in record.radiology_ids if radiology.invoice_id)
            record.total_amount = total

    def action_post(self):
        """ عند تأكيد الفاتورة، يتم ربط التحاليل والأشعة بها """
        super(LabInvoice, self).action_post()
        for record in self:
            record.lab_test_ids.write({'invoice_id': record.id})
            record.radiology_ids.write({'invoice_id': record.id})
