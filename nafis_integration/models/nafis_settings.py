from odoo import models, fields

class NafisConfig(models.Model):
    _name = 'nafis.config'
    _description = 'Nafis API Configuration'

    name = fields.Char(default="Nafis Configuration", readonly=True)
    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Client Secret")
    token_url = fields.Char(string="Token URL")
    base_url = fields.Char(string="Base URL")
    scopes = fields.Char(string="Scopes")
    test_mode = fields.Boolean(string="Test Mode")