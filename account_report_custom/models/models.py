from odoo import models

class ForceGeneralLedgerTemplate(models.Model):
    _inherit = 'account.general.ledger.report'  # مش account.report

    def _get_templates(self):
        res = super()._get_templates()
        res['main_template'] = 'account_report_custom_17_final_manual_with_test_label.general_ledger_custom_template'
        return res
