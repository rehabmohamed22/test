from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    work_location_latitude = fields.Float(
        string='Work Location Latitude',
        compute='_compute_work_location_coords',
        store=True
    )
    work_location_longitude = fields.Float(
        string='Work Location Longitude',
        compute='_compute_work_location_coords',
        store=True
    )

    @api.depends('work_location_id.latitude', 'work_location_id.longitude')
    def _compute_work_location_coords(self):
        for employee in self:
            if employee.work_location_id:
                employee.work_location_latitude = employee.work_location_id.latitude
                employee.work_location_longitude = employee.work_location_id.longitude
            else:
                employee.work_location_latitude = 0.0
                employee.work_location_longitude = 0.0
