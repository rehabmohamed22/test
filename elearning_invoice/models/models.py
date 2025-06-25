from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    student_name = fields.Char(string="Student Name")
    course_name = fields.Char(string="Course Name")
    lead_id = fields.Many2one('crm.lead', string="CRM Lead")
