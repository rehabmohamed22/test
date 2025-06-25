from odoo import models,fields,api


class Evaluation(models.Model):
    _name = 'evaluation'

    user_id = fields.Many2one('res.users', string="User", required=True)
    finished_courses = fields.Integer(string="Finished Courses", compute='_compute_finished_courses', store=True)

    course_ids = fields.Many2many('courses', string="Enrolled Courses", compute='_compute_enrolled_courses', store=True)

    @api.depends('user_id')
    def _compute_finished_courses(self):
        for record in self:
            # Get progress record for the user
            progress = self.env['progress'].search([('user_id', '=', record.user_id.id)], limit=1)
            record.finished_courses = progress.finished_courses if progress else 0

    @api.depends('user_id')
    def _compute_enrolled_courses(self):
        for record in self:
            # Get progress records for the user
            progress = self.env['progress'].search([('user_id', '=', record.user_id.id)])
            # Aggregate all courses the user is enrolled in
            record.course_ids = progress.mapped('course_ids')

    def action_view_courses(self):
        """
        This method will return an action to display the courses that the user is enrolled in.
        """
        # Get the enrolled courses for the user
        enrolled_courses = self.env['courses'].search([('user_ids', 'in', self.user_id.id)])

        # Create the action to open the courses window with a filter on the user's courses
        action = self.env.ref('roadmap_task.courses_action').read()[0]
        action['context'] = {
            'search_default_user_id': self.user_id.id,
        }
        action['domain'] = [('id', 'in', enrolled_courses.ids)]  # Filter courses by user_id
        return action


