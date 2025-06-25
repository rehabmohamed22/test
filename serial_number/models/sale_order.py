# from odoo import models, fields, api
# from num2words import num2words
#
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     amount_in_words = fields.Char(string='المبلغ بالكلمات', readonly=True, compute='_compute_amount_in_words')
#
#     def _compute_amount_in_words(self):
#         for order in self:
#             try:
#                 currency = order.currency_id
#                 amount = order.amount_total
#                 integer_part = int(amount)
#                 decimal_part = round((amount - integer_part) * 100)  # استخراج الجزء العشري
#
#                 integer_words = num2words(integer_part, lang='ar')
#
#                 if currency.name == 'USD':
#                     currency_name = "دولار"
#                     sub_currency_name = "سنت"
#                 else:
#                     currency_name = currency.currency_unit_label or currency.name
#                     sub_currency_name = currency.currency_subunit_label or "قرش"
#
#                 decimal_words = ""
#
#                 if decimal_part > 0:
#                     decimal_words = num2words(decimal_part, lang='ar')
#                     amount_in_words = f"{integer_words} {currency_name} و {decimal_words} {sub_currency_name} فقط لا غير"
#                 else:
#                     amount_in_words = f"{integer_words} {currency_name} فقط لا غير"
#
#                 order.amount_in_words = amount_in_words
#             except Exception as e:
#                 order.amount_in_words = "خطأ في التحويل"