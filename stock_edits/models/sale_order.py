from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order Inherit"

    has_price_unit_group = fields.Boolean(
        compute="compute_is_price_unit_group"
    )

    def compute_is_price_unit_group(self):
        for rec in self:
            if self.user_has_groups('stock_edits.group_sale_price_unit'):
                rec.has_price_unit_group = True
            else:
                rec.has_price_unit_group = False
