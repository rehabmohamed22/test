from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        for order in self:
            for invoice in invoices:
                if order.payment_type:
                    invoice.payment_method = order.payment_type
        return invoices
