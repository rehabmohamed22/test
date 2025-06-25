from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Order Inherit"

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('engineering_approval', 'Waiting Engineering Department Approval'),
        ('manager_approval', 'Waiting Manager Approval'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ])

    def send_to_eng_dept(self):
        self.state = 'engineering_approval'

    def action_approve(self):
        self.state = 'manager_approval'

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'manager_approval', 'engineering_approval']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
