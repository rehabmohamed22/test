from odoo import models, fields, api

class LabVisitWizard(models.TransientModel):
    _name = 'lab.visit.wizard'
    _description = 'Lab Visit Wizard'

    patient_id = fields.Many2one('lab.patient', string='Patient', required=True)
    visit_type = fields.Selection([
        ('lab_test', 'Laboratory Test'),
        ('radiology', 'Radiology Test'),
        ('both', 'Both')
    ], string='Visit Type', required=True, default='lab_test')

    def action_proceed(self):
        """ فتح الشاشة المناسبة بناءً على نوع الزيارة """
        action = False
        if self.visit_type == 'lab_test':
            action = self.env.ref('lab_management.lab_test_action').read()[0]
            action['context'] = {'default_patient_id': self.patient_id.id}
        elif self.visit_type == 'radiology':
            action = self.env.ref('lab_management.radiology_action').read()[0]
            action['context'] = {'default_patient_id': self.patient_id.id}
        elif self.visit_type == 'both':
            lab_action = self.env.ref('lab_management.lab_test_action').read()[0]
            lab_action['context'] = {'default_patient_id': self.patient_id.id}
            radiology_action = self.env.ref('lab_management.radiology_action').read()[0]
            radiology_action['context'] = {'default_patient_id': self.patient_id.id}
            return {
                'type': 'ir.actions.act_multi',
                'actions': [lab_action, radiology_action]
            }
        return action
