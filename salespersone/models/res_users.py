from odoo import models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []

        domain = [('active', '=', True)]

        # إلغاء شرط share
        domain += [('groups_id', 'in', [
            self.env.ref('base.group_user').id,
            self.env.ref('base.group_portal').id
        ])]

        users = self.search(domain + args, limit=limit)
        return users.name_get()
