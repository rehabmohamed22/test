from odoo import models, fields

class SaleReportInherit(models.Model):
    _inherit = "sale.report"

    term = fields.Char(string="Payment Method")

    def _select_additional_fields(self):

        res = super()._select_additional_fields()
        res['term'] = "partner.term"
        print(res)
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
               partner.term
               """
        print("res",res)
        return res
