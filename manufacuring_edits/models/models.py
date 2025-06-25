# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        index=True, ondelete='cascade', required=False, check_company=True)
    company_id = fields.Many2one('res.company', 'Company', related='workcenter_id.company_id')
    time_cycle = fields.Float(
        'Duration',
        compute=None,  # Explicitly detach the compute method
        help="The duration of the operation in minutes."
    )

    def add_to_bom(self):
        if 'bom_id' in self.env.context:
            bom_id = self.env.context.get('bom_id')
            self.write({'bom_id': bom_id})

    def add_operations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Select Operations to Add'),
            'res_model': 'operation.wizard',
            'view_mode': 'form',
            'domain': [],
            'context' : {
                'default_bom_id': self.id,
            },
            'target':'new'
        }

    def action_confirm(self):
        pass
class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    operation_ids = fields.Many2many('mrp.routing.workcenter')
    def add_operation(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Select Operations to Add'),
            'res_model': 'operation.wizard',
            'view_mode': 'form',
            'domain': [],
            'context': {
                'default_bom_id': self.id,
            },
            'target': 'new'
        }


class StockMove(models.Model):
    _inherit = 'stock.move'

    allowed_operation_ids = fields.Many2many(
        'mrp.routing.workcenter','rel3','col1','col2', related='raw_material_production_id.bom_id.operation_ids')
class Mrp(models.Model):
    _inherit = 'mrp.bom.byproduct'

    allowed_operation_ids = fields.Many2many('mrp.routing.workcenter','rel2','col1','col2', related='bom_id.operation_ids')


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    allowed_operation_ids = fields.Many2many('mrp.routing.workcenter','rel1','col1','col2', related='bom_id.operation_ids')
