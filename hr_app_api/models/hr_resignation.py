from odoo import models, fields, api


class HrResignation(models.Model):
    _name = 'hr.resignation'
    _description = 'Employee Resignation'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    resignation_date = fields.Date(string="Resignation Date", default=fields.Date.context_today, required=True)
    reason = fields.Text(string="Reason")
    manager_id = fields.Many2one('hr.employee', string="Manager", compute="_compute_manager", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('employee_id')
    def _compute_manager(self):
        for rec in self:
            rec.manager_id = False
            if rec.employee_id and rec.employee_id.parent_id:
                if not rec.employee_id.parent_id._origin:
                    continue
                rec.manager_id = rec.employee_id.parent_id
    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
