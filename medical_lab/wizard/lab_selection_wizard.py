from odoo import models

class LabSelectionWizard(models.TransientModel):
    _name = 'lab.selection.wizard'
    _description = 'Select Test Type'

    def open_lab_tests(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Laboratory Tests',
            'res_model': 'medical.lab.test',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def open_radiology_tests(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Radiology Tests',
            'res_model': 'medical.radiology.test',
            'view_mode': 'tree,form',
            'target': 'current',
        }
