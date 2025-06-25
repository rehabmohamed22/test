from odoo import models, api

class SaleOrderReport(models.AbstractModel):
    _name = 'sale.order.report'
    _description = "Sale Order Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            data = {}

        order_ids = data.get('orders', docids)  # تأكد أن الطلبات يتم تمريرها بشكل صحيح
        orders = self.env['sale.order'].search([('id', 'in', order_ids)])

        print("==== Report Debugging ====")
        print("Doc IDs:", docids)
        print("Data received:", data)
        print("Orders received in report:", data.get('orders'))
        print("Orders fetched from DB:", [o.id for o in orders])  # التأكد من أن الطلبات تُجلب
        print("Orders Count:", len(orders))

        if not orders:
            print("⚠ No orders found!")

        return {
            'docs': orders,
            'from_date': data.get('from_date'),
            'to_date': data.get('to_date'),
            'partner_name': data.get('partner_name', 'All Customers'),
        }