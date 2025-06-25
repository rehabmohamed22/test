from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    age = fields.Integer(string="Age")

    course_product_id = fields.Many2one(
        'product.product',
        string="Programming Course",
        domain="[('product_tmpl_id.categ_id.name', 'ilike', 'Courses')]"
    )

    education_type = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ], string="Education Type")

    source_id = fields.Many2one('lead.source', string="Came Through")
    booking_type = fields.Selection([
        ('group', 'Group'),
        ('private', 'Private'),
    ], string="Booking Type")

    guardian_name = fields.Char(string="Guardian Name")
    guardian_phone = fields.Char(string="Guardian Phone Number")
