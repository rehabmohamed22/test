from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from itertools import groupby
from operator import itemgetter

class SalesProfitReportWiz(models.TransientModel):
    _name = 'wizard.report'
    _description = 'Sales Profit Report Wizard'

    start_date = fields.Date(string='Date From', required=True)
    end_date = fields.Date(string='Date To', required=True)
    customer_id = fields.Many2many('res.partner', string='Customers', required=False)

    contract_number = fields.Many2many(
        'sale.order',
        string='Contract Number',
        domain="[('is_rental_order', '=', True),('partner_id', 'in',customer_id)]",
        required=False
    )

    def print_pdf(self):
        print("Generating report")
        if self.start_date > self.end_date:
            raise ValidationError(_("Invalid date range. Start date must be earlier than end date."))
        domain = [
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
            ('is_rental_order', '=', True)
        ]

        if self.customer_id:
            domain.append(('partner_id', 'in',self.customer_id.ids))


        if self.contract_number:
                domain.append(('id', 'in', self.contract_number.ids))
        print("Domain for sale order search:", domain)
        sale_orders = self.env['sale.order'].search(domain)

        sale_order_lines = sale_orders.mapped('order_line')
        filtered_lines = sale_order_lines.filtered(lambda line: not line.product_id.is_down_payment)
        mapped_lines = filtered_lines.mapped('order_id.partner_id')
        print(mapped_lines)
        print(filtered_lines.mapped('product_id.is_down_payment'))
        print(filtered_lines.mapped('product_id.name'))

        sale_orders_with_products = sale_orders.filtered(
            lambda so: any(line in filtered_lines for line in so.order_line))

        if not sale_orders_with_products:
            raise ValidationError(_('No sale orders found for the given date range and customer.'))
        return self.env.ref('pivot.report_action_pdf').report_action(sale_orders_with_products)

    def print_pdf_detail(self):
        print("Generating report")

        if self.start_date > self.end_date:
            raise ValidationError(_("Invalid date range. Start date must be earlier than end date."))

        domain = [
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
            ('is_rental_order', '=', True)
        ]


        if self.customer_id:
            domain.append(('partner_id', 'in', self.customer_id.ids))

        if self.contract_number:
            domain.append(('id', 'in', self.contract_number.ids))

        print("Domain for sale order search:", domain)
        sale_orders = self.env['sale.order'].search(domain)

        sale_order_lines = sale_orders.mapped('order_line')
        filtered_lines = sale_order_lines.filtered(lambda line: not line.product_id.is_down_payment)

        print(filtered_lines.mapped('product_id.is_down_payment'))
        print(filtered_lines.mapped('product_id.name'))

        sale_orders_with_products = sale_orders.filtered(
            lambda so: any(line in filtered_lines for line in so.order_line))

        if not sale_orders_with_products:
            raise ValidationError(_('No sale orders found for the given date range and customer.'))
        return self.env.ref('pivot.report_action_detail_pdf').report_action(sale_orders_with_products)

