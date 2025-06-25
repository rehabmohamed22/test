from odoo import models, fields

class SelectLabTypeWizard(models.TransientModel):
    _name = 'select.lab.type.wizard'
    _description = 'Select Laboratory Test Type'

    lab_type = fields.Selection([
        ('lab_test', 'Laboratory Test'),
        ('imaging_test', 'Imaging Test')
    ], string="Test Type", required=True, default='lab_test')

    def action_proceed(self):
        """Redirect user to the appropriate screen based on selection"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Laboratory Tests' if self.lab_type == 'lab_test' else 'Imaging Tests',
            'res_model': 'lab.test.type' if self.lab_type == 'lab_test' else 'lab.imaging.type',
            'view_mode': 'tree,form',
            'target': 'current',
        }
