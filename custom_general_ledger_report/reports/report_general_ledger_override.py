from odoo import models
from odoo.addons.account_reports.report.general_ledger import GeneralLedgerReport

class CustomGeneralLedgerReport(GeneralLedgerReport):

    def _get_templates(self):
        templates = super()._get_templates()
        templates['main_template'] = 'custom_general_ledger_report.custom_general_ledger_main_template'
        return templates

    def _get_report_values(self, options):
        res = super()._get_report_values(options)
        res['date_from'] = options.get('date', {}).get('date_from')
        res['date_to'] = options.get('date', {}).get('date_to')
        return res
