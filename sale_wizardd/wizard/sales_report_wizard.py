from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _description = 'Sale Report Wizard'

    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")

    def action_generate_report(self):
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['sale', 'done'])  # تأكيد تضمين الأوامر المؤكدة فقط
        ]
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))

        sale_orders = self.env['sale.order'].search(domain)

        if not sale_orders:
            raise ValidationError('No sale orders found for the given date range and customer.')

        print("\n🔍 عدد أوامر البيع المسترجعة:", len(sale_orders))

        # استدعاء التقرير وتمرير البيانات بشكل صحيح
        return self.env.ref('sale_wizardd.action_sale_report').report_action(sale_orders)
