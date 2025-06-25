from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Sale Order Report Wizard'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer")

    def action_print_report(self):
        domain = [('date_order', '>=', self.from_date), ('date_order', '<=', self.to_date)]
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))

        orders = self.env['sale.order'].search(domain)

        if not orders:
            raise UserError("No orders found in the specified date range.")

        data = {
            'orders': orders.ids,  # تمرير المعرفات فقط
            'from_date': self.from_date,
            'to_date': self.to_date,
            'partner_name': self.partner_id.name if self.partner_id else "All Customers",
        }

        print("==== Wizard Debugging ====")
        print("Orders found:", orders)
        print("Orders IDs:", orders.ids)
        print("Data sent to report:", data)

        return self.env.ref('sale_wizard.sale_order_report').report_action([], data=data)
