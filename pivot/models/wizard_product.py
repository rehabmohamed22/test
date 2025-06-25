from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductReportWiz(models.TransientModel):
    _name = 'product.wizard.report'
    _description = 'Product Report Wizard'

    product_category = fields.Many2many(
        'product.category',
        string='Product Category'
    )
    product_id = fields.Many2many(
        'product.template',
        string='Product'
    )
    rental_order_type = fields.Selection(
        [('شاغر', 'شاغر'), ('مؤجر', 'مؤجر')],
        string="Product Status"
    )

    @api.onchange('product_category')
    def _onchange_product_category(self):
        if self.product_category:
            product_domain = [('categ_id', 'in', self.product_category.ids)]
            self.product_id = self.env['product.template'].search(product_domain)
        else:
            self.product_id = False

    @api.onchange('rental_order_type')
    def _onchange_rental_order_type(self):
        if self.rental_order_type:
            product_domain = [('rental_order_type', '=', self.rental_order_type)]
            if self.product_category:
                product_domain.append(('categ_id', 'in', self.product_category.ids))
            self.product_id = self.env['product.template'].search(product_domain)
        else:
            self.product_id = False

    def generate_product_report(self):
        domain = []

        if self.product_category:
            domain.append(('categ_id', 'in', self.product_category.ids))

        if self.product_id:
            domain.append(('id', 'in', self.product_id.ids))

        if self.rental_order_type:
            domain.append(('rental_order_type', '=', self.rental_order_type))

        _logger.debug("Domain for product search: %s", domain)

        products = self.env['product.template'].search(domain)

        if not products:
            raise ValidationError(_('No products found for the given criteria.'))

        return self.env.ref('pivot.report_product_action_detail_pdf').report_action(products)
