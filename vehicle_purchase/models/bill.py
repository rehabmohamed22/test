from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    extra_fees = fields.Monetary(
        string="Another Fees",
        currency_field='currency_id',
        default=0.0,
        help="Additional fees included in the subtotal, not included in tax base."
    )

    @api.depends('quantity', 'price_unit', 'discount', 'tax_ids', 'extra_fees')
    def _compute_amount(self):
        """
        تعديل احتساب الضرائب ليتم حسابها فقط على المبلغ الخاضع للضريبة.
        """
        super(AccountMoveLine, self)._compute_amount()
        for line in self:
            if line.extra_fees and line.tax_ids:
                # السعر قبل الضريبة بعد الخصومات
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                base = price * line.quantity
                base_for_tax = base - (line.extra_fees or 0.0)
                if base_for_tax < 0:
                    base_for_tax = 0.0

                # إعادة حساب الضريبة
                taxes = line.tax_ids.compute_all(
                    price,
                    line.currency_id,
                    line.quantity,
                    product=line.product_id,
                    partner=line.partner_id
                )
                # الفرق بين الضريبة الأصلية والجديدة
                original_tax = taxes['total_included'] - taxes['total_excluded']

                # الضريبة الجديدة فقط على base_for_tax
                taxes_for_base = line.tax_ids.compute_all(
                    base_for_tax / (line.quantity or 1.0),  # السعر الجديد للوحدة
                    line.currency_id,
                    line.quantity,
                    product=line.product_id,
                    partner=line.partner_id
                )
                new_tax = taxes_for_base['total_included'] - taxes_for_base['total_excluded']

                # تحديث القيم
                line.tax_base_amount = base_for_tax
                line.tax_amount = new_tax
                # تعديل الإجمالي
                line.price_total = base + new_tax
                # تعديل السعر الفرعي بدون ضريبة
                line.price_subtotal = base