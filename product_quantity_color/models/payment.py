# from odoo import models, fields, api
#
#
# class AccountPayment(models.Model):
#     _inherit = 'account.payment'
#
#     journal_id = fields.Many2one('account.journal', string="Journal")
#     payment_type = fields.Selection([
#         ('outbound', 'سند صرف'),
#         ('inbound', 'سند استلام'),
#     ], string="Payment Type")
#
#     @api.onchange('journal_id')
#     def _onchange_journal_id(self):
#         # طباعة قيمة الـ journal_id عند التغيير
#         print(f"تم تغيير journal_id إلى: {self.journal_id.name}")
#
#         if self.journal_id:
#             if self.journal_id.type == 'bank':
#                 print("تم اختيار نوع الـ journal كـ Bank")
#                 self._set_bank_payment_labels()
#             elif self.journal_id.type == 'cash':
#                 print("تم اختيار نوع الـ journal كـ Cash")
#                 self._set_cash_payment_labels()
#             else:
#                 print("تم اختيار نوع journal غير محدد.")
#         else:
#             print("لم يتم اختيار journal.")
#
#     def _set_bank_payment_labels(self):
#         # تغيير تسميات الـ payment_type عندما يكون الـ journal هو Bank
#         print("تغيير تسميات الـ payment_type إلى خيارات بنك")
#         self._fields['payment_type'].selection = [
#             ('outbound', 'سند صرف بنك'),
#             ('inbound', 'سند استلام بنك'),
#         ]
#         print(f"القيم المتاحة في payment_type هي: {self._fields['payment_type'].selection}")
#
#     def _set_cash_payment_labels(self):
#         # تغيير تسميات الـ payment_type عندما يكون الـ journal هو Cash
#         print("تغيير تسميات الـ payment_type إلى خيارات كاش")
#         self._fields['payment_type'].selection = [
#             ('outbound', 'سند صرف كاش'),
#             ('inbound', 'سند استلام كاش'),
#         ]
#         print(f"القيم المتاحة في payment_type هي: {self._fields['payment_type'].selection}")