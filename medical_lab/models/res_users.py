from odoo import models, fields

class ResUsers(models.Model):
    _inherit = "res.users"

    medical_lab_doctor = fields.Boolean(string="Is a Medical Lab Doctor")
