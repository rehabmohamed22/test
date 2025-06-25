from email.policy import default
from pkg_resources import require

from odoo import models, fields, api

class Courses(models.Model):
    _name = 'courses'

    name = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    link = fields.Char()
    description = fields.Text()
    number_of_videos = fields.Integer()
    progress_ids = fields.One2many(
        'progress', 'course_id', string="Progress"
    )
    user_ids = fields.Many2many(
        'res.users', string="Enrolled Users", compute='_compute_enrolled_users', store=True
    )

    @api.depends('progress_ids.user_id')
    def _compute_enrolled_users(self):
        for course in self:
            course.user_ids = course.progress_ids.mapped('user_id')



class CoursesLine(models.Model):
    _name = 'courses.line'

    description = fields.Char()
    course_id = fields.Many2one('courses')

