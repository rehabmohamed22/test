from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    created_by_user = fields.Many2one(
        comodel_name='res.users',
        string='Created By',
        compute='_compute_created_by_user',
        store=False
    )

    def _compute_created_by_user(self):
        for rec in self:
            rec.created_by_user = rec.create_uid

    @api.model
    def notify_low_stock_products(self):
        low_stock_points = self.search([])

        for rec in low_stock_points:
            try:
                product = rec.product_id
                qty_available = product.qty_available
                min_qty = rec.product_min_qty

                if qty_available < min_qty:
                    self.env['mail.message'].create({
                        'subject': "Stock Alert: Product Below Minimum Quantity",
                        'body': f"""
                            <p><strong>Alert!</strong></p>
                            <p>The product <strong>{product.display_name}</strong> has low stock.</p>
                            <ul>
                                <li>Available: {qty_available}</li>
                                <li>Minimum Required: {min_qty}</li>
                            </ul>
                        """,
                        'message_type': 'notification',
                        'subtype_id': self.env.ref('mail.mt_comment').id,
                        'res_id': rec.id,
                        'model': self._name,
                        'author_id': self.env.user.partner_id.id,
                        'notification_ids': [(0, 0, {
                            'res_partner_id': rec.created_by_user.partner_id.id,
                            'notification_type': 'inbox'
                        })],
                    })

            except Exception as e:
                _logger.warning(f"Error sending notification for {rec.product_id.name}: {e}")
