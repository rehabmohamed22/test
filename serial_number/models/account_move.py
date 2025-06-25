from odoo import models, fields, api
from num2words import num2words

class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_in_words = fields.Char(string='المبلغ بالكلمات', readonly=True, compute='_compute_amount_in_words')

    def _compute_amount_in_words(self):
        for invoice in self:
            try:
                currency = invoice.currency_id
                amount = invoice.amount_total
                integer_part = int(amount)
                decimal_part = round((amount - integer_part) * 100)

                integer_words = num2words(integer_part, lang='ar')

                if currency.name == 'USD':
                    currency_name = "دولار"
                    sub_currency_name = "سنت"
                else:
                    currency_name = currency.currency_unit_label or currency.name
                    sub_currency_name = currency.currency_subunit_label or "قرش"

                decimal_words = ""

                if decimal_part > 0:
                    decimal_words = num2words(decimal_part, lang='ar')
                    amount_in_words = f"{integer_words} {currency_name} و {decimal_words} {sub_currency_name} فقط لا غير"
                else:
                    amount_in_words = f"{integer_words} {currency_name} فقط لا غير"

                invoice.amount_in_words = amount_in_words
            except Exception as e:
                invoice.amount_in_words = "خطأ في التحويل"