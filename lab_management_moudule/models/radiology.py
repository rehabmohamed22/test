from odoo import models, fields, api


class LabRadiology(models.Model):
    _name = 'lab.radiology'
    _description = 'Radiology Test'
    _rec_name = 'radiology_name'

    radiology_name = fields.Char(string='Radiology Name', required=True)
    radiology_code = fields.Char(string='Radiology Code', required=True)

    patient_id = fields.Many2one('lab.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('lab.doctor', string='Doctor', required=True)

    result_file = fields.Binary(string='Result File', attachment=True)
    result_filename = fields.Char(string="Result File Name")

    result_description = fields.Text(string='Radiology Report')
    result_status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], string='Result Status', default='pending')

    date_requested = fields.Date(string='Date Requested', default=fields.Date.context_today)
    date_completed = fields.Date(string='Date Completed')

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    def mark_as_completed(self):
        """ تحديث حالة الأشعة إلى مكتملة """
        for record in self:
            record.result_status = 'completed'
            record.date_completed = fields.Date.today()
