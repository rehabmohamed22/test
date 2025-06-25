from odoo import models, fields, api

class HrExpenseRequest(models.Model):
    _name = 'hr.expense.request'
    _description = 'Expense Request'

    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True)
    amount = fields.Float(string='المبلغ', required=True)
    reason = fields.Text(string='السبب', required=True)
    request_date = fields.Date(string='تاريخ الطلب', default=fields.Date.today)
    state = fields.Selection([
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    ], string='الحالة', default='pending')
