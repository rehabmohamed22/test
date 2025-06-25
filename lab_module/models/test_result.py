from odoo import models, fields, api

class LabTestResult(models.Model):
    _name = 'lab.test.result'
    _description = 'Lab Test Result'
    _order = 'date_done desc'

    name = fields.Char(string="Result Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: 'New')
    request_id = fields.Many2one('lab.test.request', string="Test Request", required=True, ondelete='cascade')
    patient_id = fields.Many2one('lab.patient', string="Patient", related='request_id.patient_id', store=True)
    test_id = fields.Many2one('lab.test', string="Test", required=True)
    result_value = fields.Char(string="Result Value")
    normal_range = fields.Char(string="Normal Range", related='test_id.normal_range', store=True)
    date_done = fields.Datetime(string="Date Done", default=fields.Datetime.now, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated')
    ], string="Status", default='draft', required=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lab.test.result') or 'New'
        return super(LabTestResult, self).create(vals)

    def action_validate(self):
        self.write({'state': 'validated'})
