from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    enrolled_courses_count = fields.Integer(
        string="Enrolled Courses",
        compute='_compute_enrolled_courses_count',
        store=True
    )

    @api.depends('progress_ids')
    def _compute_enrolled_courses_count(self):
        for user in self:
            user.enrolled_courses_count = len(user.progress_ids)

    progress_ids = fields.One2many('progress', 'user_id', string="Progress")
