from odoo import models, fields
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_create_invoice(self):
        for lead in self:
            if not lead.partner_id:
                raise UserError("Please set the student (customer) first.")
            if not lead.course_product_id:
                raise UserError("Please select a course for the student.")

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': lead.partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': lead.course_product_id.name,
                    'quantity': 1,
                    'price_unit': lead.course_product_id.lst_price,
                    'product_id': lead.course_product_id.id,
                })],
                'invoice_origin': lead.name,
            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoice.id,
                'target': 'current',
            }