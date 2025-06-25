from odoo import fields,models,api
from odoo.exceptions import ValidationError

class PublicHoliday(models.Model):
    _name = 'public.holiday'

    descriptioon = fields.Char(string="Descriptioon")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),], default='draft',
        string='Status',)
    apply_on = fields.Selection(
        string='Apply on',
        selection=[('employee', 'Employee'),
                   ('department', 'Department'),
                   ('tags','Tags') ],)
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    notes = fields.Char(
        string='Notes',
        required=False)

    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="public_holiday_hr_employee_rel",
        column1="holiday_id",
        column2="employee_id",
        string="Employees"
    )

    department_ids = fields.Many2many(
        comodel_name="hr.department",
        relation="public_holiday_hr_department_rel",
        column1="holiday_id",
        column2="department_id",
        string="Departments"
    )

    tags_ids = fields.Many2many(comodel_name="hr.employee.category",string="Tags", )

    @api.constrains('date_start', 'date_end')
    def _check_date_range(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("End Date must be after Start Date.")

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_approve(self):
        self.write({'state': 'approve'})

    def action_refuse(self):
        self.write({'state': 'refuse'})

