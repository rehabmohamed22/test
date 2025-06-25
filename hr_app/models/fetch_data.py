from odoo import fields,models,api
from odoo import api, models, fields,SUPERUSER_ID


class FetchData(models.Model):
    _name = 'fetch.data'
    _description = 'Hospital Api'

    model_api = fields.Many2one(comodel_name="ir.model", string="Api Model" )
    model_name=fields.Char(related="model_api.model",store=True)
    fields_api = fields.Many2many(comodel_name="ir.model.fields", string="fields_api",domain="[('model_id','=',model_api)]" )

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#
#     def create_order(self, vals):
#         with self.pool.cursor() as cr:
#             res = self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).create(vals)
#             return res
#
#
#
#     def update_order(self, vals):
#         with self.pool.cursor() as cr:
#             res = self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).write(vals)
#             return res