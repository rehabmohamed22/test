# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_taxes = fields.Float(compute='set_total_taxes',stored=True)
    total_discount = fields.Float(
        string='Total Discount',
        compute='_compute_total_discount',
        store=True
    )
    @api.depends('order_line.discount', 'order_line.price_subtotal')
    def _compute_total_discount(self):
        for move in self:
            total_discount = 0.0
            for line in move.order_line:
                discount_amount = (line.price_unit * line.product_qty * (line.discount / 100))
                total_discount += discount_amount
            move.total_discount = total_discount

    @api.depends('order_line.taxes_id', 'order_line.price_unit')
    def set_total_taxes(self):
        for record in self:
            total = 0.0
            for line in record.order_line:
                for tax in line.taxes_id:
                    total += line.price_unit * (tax.amount / 100)
            record.total_taxes = total

    def convert_amount_words(self):
        pre = float(self.amount_total)
        text_ar = ' '
        text_en = ' '

        entire_num = int(pre)
        decimal_num = int(round(pre % 1, 2) * 100)

        currency_mapping = {
            'SDG': ['جنيه', 'قرش', 'قروش'],
            'AED': ['درهم', 'فلس', 'فلسات'],
            'CFA': ['فرنك', 'سنت', 'سنتات'],
            'EGP': ['جنيه', 'قرش', 'قروش'],
            'EUR': ['يورو', 'سنت', 'سنتات'],
            'USD': ['دولار', 'سنت', 'سنتات'],
            'SSP': ['جنيه', 'قرش', 'قروش'],
            'SAR': ['ريال', 'هللة', 'هللات'],
            'CNY': ['يوان', 'فين', 'فينات'],
            'KWD': ['دينار', 'فلس', 'فلسات'],
            'OMR': ['ريال', 'بيسة', 'بيسات'],
            'QAR': ['ريال', 'درهم', 'درهمات'],
            'BHD': ['دينار', 'فلس', 'فلسات'],
            'JOD': ['دينار', 'قرش', 'قروش'],
            'YER': ['ريال', 'فلس', 'فلسات']
        }
        currency_mapping_en = {
            'SDG': ['Pound', 'Piastre', 'Piastres'],
            'AED': ['Dirham', 'Fils', 'Fils'],
            'CFA': ['Franc', 'Centime', 'Centimes'],
            'EGP': ['Pound', 'Piastre', 'Piastres'],
            'EUR': ['Euro', 'Cent', 'Cents'],
            'USD': ['Dollar', 'Cent', 'Cents'],
            'SSP': ['Pound', 'Piastre', 'Piastres'],
            'SAR': ['Riyal', 'Halalah', 'Halalahs'],
            'CNY': ['Yuan', 'Fen', 'Fens'],
            'KWD': ['Dinar', 'Fils', 'Fils'],
            'OMR': ['Rial', 'Baisa', 'Baisas'],
            'QAR': ['Riyal', 'Dirham', 'Dirhams'],
            'BHD': ['Dinar', 'Fils', 'Fils'],
            'JOD': ['Dinar', 'Piastre', 'Piastres'],
            'YER': ['Rial', 'Fils', 'Fils']
        }

        currency = self.currency_id.name
        currency_name = currency_mapping.get(currency, ['عملة', 'وحدة', 'وحدات'])
        currency_name_en = currency_mapping_en.get(currency, ['coin', 'unit', 'units'])
        print(currency_name[0])

        text_ar += num2words(entire_num, lang='ar') + ' ' + currency_name[0]
        text_en += num2words(entire_num, lang='en') + ' ' + currency_name_en[0]

        if decimal_num > 0:
            text_ar += ' و ' + num2words(decimal_num, lang='ar') + ' ' + currency_name[1]
        if decimal_num > 0:
            text_en += ' and ' + num2words(decimal_num, lang='en') + ' ' + currency_name_en[1]
        return {
            'text_ar':text_ar,
            'text_en':text_en
        }
