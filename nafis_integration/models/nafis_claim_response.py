from odoo import models, fields

class NafisClaimResponse(models.Model):
    _name = 'nafis.claim.response'
    _description = 'Response from Nafis for Claim'

    claim_id = fields.Many2one('nafis.claim', string="Related Claim", required=True, ondelete="cascade")
    status = fields.Char(string="Status")
    message = fields.Text(string="Message")
    approved_amount = fields.Float(string="Approved Amount")
    full_response = fields.Text(string="Full JSON Response")
    create_date = fields.Datetime(string="Response Time", readonly=True)
