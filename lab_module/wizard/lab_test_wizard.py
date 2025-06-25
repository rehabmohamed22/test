from odoo import models, fields, api

class LabTestWizard(models.TransientModel):
    _name = 'lab.test.wizard'
    _description = 'Lab Test Selection Wizard'

    test_type = fields.Selection([
        ('analysis', 'Laboratory Analysis'),
        ('radiology', 'Radiology Test')
    ], string="Test Type", required=True, default='analysis')

    def action_proceed(self):
        """ Redirect to the correct form view based on the selected test type """
        if self.test_type == 'analysis':
            return {
                'type': 'ir.actions.act_window',
                'name': 'Lab Analysis Request',
                'res_model': 'lab.test.request',
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Radiology Test Request',
                'res_model': 'lab.radiology.request',
                'view_mode': 'form',
                'target': 'current',
            }
