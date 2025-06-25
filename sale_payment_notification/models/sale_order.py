from odoo import models, api
from datetime import timedelta,date
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def send_notification_for_payment_cron(self):
        orders = self.env['sale.order'].search([
            ('payment_term_id', '!=', False),
            ('date_order', '!=', False),
            ('state', 'in', ['sale', 'done'])
        ], limit=1)

        for order in orders:
            try:
                days_str = ''.join(filter(str.isdigit, order.payment_term_id.name or ''))
                if not days_str:
                    continue

                days = int(days_str)
                after_payment_term_days = order.create_date + timedelta(days=days)
                print(after_payment_term_days)
                if date.today() >= after_payment_term_days:
                    self.env['mail.message'].create({
                        'subject': "New Internal Review Notification",
                        'body': "Payment Due. Please Contact Customer For Payment.",
                        'message_type': 'notification',
                        'subtype_id': self.env.ref('mail.mt_comment').id,
                        'res_id': order.id,
                        'model': self._name,
                        'author_id': self.env.user.partner_id.id,
                        'notification_ids': [(0, 0, {
                            'res_partner_id': self.user_id.partner_id.id,
                            'notification_type': 'inbox'
                        })],
                    })

            except Exception as e:
                _logger.warning(f"Could not schedule activity for SO {order.name}: {e}")