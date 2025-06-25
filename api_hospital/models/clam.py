# from odoo import fields,models,api
# from odoo.tools.populate import compute
#
#
# class Clam(models.Model):
#     _name = 'clam'
#     _inherit = ['mail.thread','mail.activity.mixin']
#
#     partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
#     date = fields.Date(string="Date" )
#     clam_lines = fields.One2many(comodel_name="clam.line", inverse_name="clam_id", string="Clam Lines" )
#
# class ClamLine(models.Model):
#     _name = 'clam.line'
#
#     clam_id = fields.Many2one(comodel_name="clam", string="Clam" )
#
#     product_id = fields.Many2one(comodel_name="product.product", string="Product")
#     notes = fields.Char(string="Notes")
#     total_price = fields.Float(string="Total Price")
#     loading_ratio = fields.Float(string="Loading Ratio")
#
#     subtotal = fields.Float(string="Subtotal",compute="_compute_subtotal",store=True)
#
#     patient = fields.Many2one(comodel_name="res.partner", string="Patient")
#     doctor = fields.Many2one(comodel_name="res.partner", string="Doctor")
#
#     @api.depends('total_price', 'loading_ratio')
#     def _compute_subtotal(self):
#         for rec in self:
#             total_price = rec.total_price or 0.0  # التأكد من عدم وجود None
#             loading_ratio = rec.loading_ratio or 0.0  # التأكد من عدم وجود None
#             rec.subtotal = (loading_ratio / 100) * total_price if total_price and loading_ratio else 0.0
#
#
#
#
#
#
#
#
