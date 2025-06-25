from odoo import models, fields

class JwtTokenBlacklist(models.Model):
    _name = 'jwt.token.blacklist'
    _description = 'JWT Token Blacklist'

    token = fields.Text(string="Token", required=True)
    blacklisted_at = fields.Datetime(string="Blacklisted At", default=fields.Datetime.now)
