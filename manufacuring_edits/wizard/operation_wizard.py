from odoo import models, fields, api

class Operations(models.TransientModel):
    _name = 'operation.wizard'


    operation_ids = fields.Many2many('mrp.routing.workcenter')
    bom_id = fields.Many2one('mrp.bom')
    def action_confirm(self):
        self.bom_id.operation_ids = [(6,0,self.operation_ids.ids)]