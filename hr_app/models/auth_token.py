from odoo import models, fields, api

class AuthToken(models.Model):
    _name = 'auth.token'
    _description = 'JWT Tokens Whitelist'

    user_id = fields.Many2one('res.users', required=True, string='User')
    token = fields.Text(required=True, string='JWT Token')
    expiration = fields.Datetime(required=True, string='Expiration Date')
