from odoo import models

class GeneralLedgerTemplateOverride(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    def _get_templates(self):
        return {
            'main_template': 'gl_report_date_range_clean.general_ledger_custom_template',
            'line_template': 'account_reports.line_template',
        }
