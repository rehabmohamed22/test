from odoo import models

class ReportJournalEntry(models.AbstractModel):
    _name = 'report_journal_entry'
    _description = 'Journal Entry Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'docs': docs,
        }