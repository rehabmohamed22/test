from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template Inherit"

    @api.constrains('default_code', 'company_id')
    def _check_unique_default_code_per_company(self):
        for product in self:
            if product.default_code:
                existing_product = self.env['product.template'].sudo().search([
                    ('default_code', '=', product.default_code),
                    '|', ('company_id', '=', product.company_id.id), ('company_id', '=', False),
                    ('id', '!=', product.id)
                ])
                if existing_product:
                    raise ValidationError("Internal Reference must be unique per product.")
