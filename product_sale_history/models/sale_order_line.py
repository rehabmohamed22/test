from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def open_line_wizard(self):
        """فتح الـ Wizard لعرض تفاصيل السطر المحدد"""
        return {
            'name': 'تفاصيل المنتج',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('detailes_button.sale_order_line_wizard_form').id,
            'target': 'new',
            'context': {
                'active_id': self.id,  # تمرير ID السطر المحدد فقط
            }
        }
