from odoo import models

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_print_student_invoice(self):
        return self.env.ref('basma_invoice_custom.action_report_crm_invoice').report_action(self)
