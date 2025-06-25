from odoo import models
from odoo.addons.account_reports.report.general_ledger import GeneralLedgerReport

class CustomGeneralLedgerReport(GeneralLedgerReport):

    def get_header(self, options, report_manager=None):
        header = super().get_header(options, report_manager=report_manager)

        date_from = options.get('date', {}).get('date_from')
        date_to = options.get('date', {}).get('date_to')

        if date_from and date_to:
            period_html = f"<p style='margin-bottom:10px; font-size:14px;'><strong>Period:</strong> {date_from} → {date_to}</p>"
            return period_html + header

        return header
