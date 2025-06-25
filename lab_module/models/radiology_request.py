# from odoo import models, fields, api
#
# class RadiologyRequest(models.Model):
#     _name = 'lab.radiology.request'
#     _description = 'Radiology Request'
#
#     name = fields.Char(string="Request Reference", required=True, copy=False, readonly=True, default='New')
#     patient_id = fields.Many2one('lab.patient', string="Patient", required=True)
#     doctor_id = fields.Many2one('lab.doctor', string="Doctor", required=True)
#     radiology_test_ids = fields.Many2many('lab.radiology.test', string="Radiology Tests")
#     state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')
#
#     @api.model
#     def create(self, vals):
#         if vals.get('name', 'New') == 'New':
#             vals['name'] = self.env['ir.sequence'].next_by_code('lab.radiology.request') or 'New'
#         return super(RadiologyRequest, self).create(vals)
