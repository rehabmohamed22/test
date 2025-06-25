# models/public_holiday.py
from odoo import models, fields, api


class PublicHoliday(models.Model):
    _name = 'public.holiday'
    _description = 'Public Holiday'

    name = fields.Char(string="Holiday Name", required=True)

    apply_on_employee = fields.Many2one('hr.employee', string="Employee")
    apply_on_department = fields.Many2one('hr.department', string="Department")
    apply_on_tags = fields.Many2many('hr.employee.category', string="Tags")

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)

    number_of_days = fields.Float(string="Days", compute="_compute_days", store=True)
    notes = fields.Text(string="Reason")
    state = fields.Selection([
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string="Status", default='to_approve')

    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                delta = (rec.date_to - rec.date_from).days + 1
                rec.number_of_days = max(delta, 0)
            else:
                rec.number_of_days = 0

    def action_approve(self):
        for record in self:
            record.state = 'approved'

    def action_refuse(self):
        for record in self:
            record.state = 'refused'
