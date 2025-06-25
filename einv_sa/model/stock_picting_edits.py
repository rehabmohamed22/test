from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    #
    # arabic_project_name_ids = fields.Many2many(
    #     'project.name',
    #     'rel_arabic_project_name_picking',
    #     'picking_id',
    #     'project_id',
    #     string="Arabic Projects",
    #     help="Select one or more Arabic projects."
    # )
    #
    #
    # english_project_name_ids = fields.Many2many(
    #     'project.name',
    #     'rel_en_project_name_picking',
    #     'picking_id',
    #     'project_id',
    #     string="English Projects",
    #     help="Select one or more English projects."
    # )
    #
    # combined_project_name_ids = fields.Many2many(
    #     'project.name',
    #     'rel_combined_project_name_picking',
    #     'picking_id',
    #     'project_id',
    #     string="Projects",
    #     help="Select both Arabic and English projects."
    # )
    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id:
    #         ar_projects = self.partner_id.ar_project_name.ids if self.partner_id.ar_project_name else []
    #         en_projects = self.partner_id.project_name.ids if self.partner_id.project_name else []
    #
    #         self.arabic_project_name_ids = [(6, 0, ar_projects)]
    #         self.english_project_name_ids = [(6, 0, en_projects)]
    #         self.combined_project_name_ids = [(6, 0, ar_projects + en_projects)]
