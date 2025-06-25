from odoo import models , api , fields
class Progress(models.Model):
    _name = 'progress'
    _rec_name = 'user_id'

    course_ids = fields.Many2many(
        'courses', 'course_progress_rel', 'progress_id', 'course_id', string="Courses"
    )
    user_id = fields.Many2one('res.users', required=True)
    finished_courses = fields.Integer(default=0,store=1)
    total_videos = fields.Integer(compute='_compute_total_videos', store=True)
    progress = fields.Float(compute='_compute_progress', store=True)
    course_id = fields.Many2one('courses', string="Course", required=True)
    finished_videos = fields.Integer(string="Finished Videos", default=0)

    @api.depends('course_ids.number_of_videos')
    def _compute_total_videos(self):
        for record in self:
            record.total_videos = sum(record.course_ids.mapped('number_of_videos'))

    @api.depends('finished_videos', 'total_videos')
    def _compute_progress(self):
        for record in self:
            if record.total_videos:
                record.progress = (record.finished_videos / record.total_videos) * 100
            else:
                record.progress = 0
