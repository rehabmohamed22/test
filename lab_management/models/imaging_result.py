from odoo import models, fields

class ImagingResult(models.Model):
    _name = 'lab.imaging.result'
    _description = 'Imaging Test Result'

    visit_id = fields.Many2one('lab.patient.visit', string='Patient Visit', ondelete='cascade', required=True)
    imaging_type_id = fields.Many2one('lab.imaging.type', string='Imaging Test', required=True)
    report = fields.Text(string='Report', required=True)
    attachment = fields.Binary(string='Attachment', attachment=True)
    findings = fields.Text(string="Findings")
    notes = fields.Text(string="Notes")