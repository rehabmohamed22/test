from odoo import models, fields, api
from odoo.exceptions import MissingError

class HrResignation(models.Model):
    _name = 'hr.resignation'
    _description = 'Employee Resignation'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    resignation_date = fields.Date(string="Resignation Date", default=fields.Date.context_today, required=True)
    reason = fields.Text(string="Reason")
    manager_id = fields.Many2one('hr.employee', string="Manager", compute="_compute_employee_info", store=True)
    contract_id = fields.Many2one('hr.contract', string="Contract", compute="_compute_employee_info", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    # @api.depends('employee_id')
    # def _compute_employee_info(self):
    #     for rec in self:
    #         rec.manager_id = False
    #         rec.contract_id = False
    #
    #         employee = rec.employee_id
    #         if employee and not employee._is_missing():
    #             if employee.parent_id and not employee.parent_id._is_missing():
    #                 rec.manager_id = employee.parent_id
    #
    #             contract = self.env['hr.contract'].search([
    #                 ('employee_id', '=', employee.id),
    #                 ('state', '=', 'open')
    #             ], limit=1, order='date_start desc')
    #
    #             if contract and not contract._is_missing():
    #                 rec.contract_id = contract

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'