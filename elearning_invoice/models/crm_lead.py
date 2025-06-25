from odoo import models, fields

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    programming_course_id = fields.Many2one('product.product', string="Programming Course")

    def action_create_invoice(self):
        self.ensure_one()

        course = self.course_product_id

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'student_name': self.name,
            'course_name': course.name if course else '',
            'lead_id': self.id,
        }

        invoice = self.env['account.move'].create(invoice_vals)

        if course:
            invoice.write({
                'invoice_line_ids': [(0, 0, {
                    'product_id': course.id,
                    'quantity': 1,
                    'price_unit': course.lst_price,
                })]
            })

        # ✅ فتح نموذج الفاتورة مباشرة (وليس التقرير)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
