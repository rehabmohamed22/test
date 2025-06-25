# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    """Extend to add fields."""

    _inherit = 'res.partner'

    brand_id = fields.Many2one(
        'res.partner.brand',
        string="Brand",
    )
