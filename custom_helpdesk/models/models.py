from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    project_code = fields.Char(string="Project Code")


    def send_ticket(self):
        pass

class HelpdeskTicketStage(models.Model):
    _inherit = 'helpdesk.stage'

    is_new = fields.Boolean(string="Is New", compute='_compute_stage_state', default=False)
    is_in_progress = fields.Boolean(string="Is In Progress", compute='_compute_stage_state', default=False)
    is_on_hold = fields.Boolean(string="Is On Hold", compute='_compute_stage_state', default=False)
    is_done = fields.Boolean(string="Is Done", compute='_compute_stage_state', default=False)
    is_cancelled = fields.Boolean(string="Is Cancelled", compute='_compute_stage_state', default=False)

    @api.depends('name')
    def _compute_stage_state(self):
        for stage in self:
            stage.is_new = False
            stage.is_in_progress = False
            stage.is_on_hold = False
            stage.is_done = False
            stage.is_cancelled = False

            if stage.name == 'New':
                stage.is_new = True
            elif stage.name == 'In Progress':
                stage.is_in_progress = True
            elif stage.name == 'On Hold':
                stage.is_on_hold = True
            elif stage.name == 'Done':
                stage.is_done = True
            elif stage.name == 'Cancelled':
                stage.is_cancelled = True
