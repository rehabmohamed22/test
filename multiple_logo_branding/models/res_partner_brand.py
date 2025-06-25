# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartnerBrand(models.Model):
    """Partner Brand Model."""

    _name = 'res.partner.brand'
    _description = 'Partner Brand'

    name = fields.Char(
        string="Brand Name",
        required=True,
        index=True,
        copy=False,
    )
    logo = fields.Image(
        string="Logo",
        required=True,
        copy=False,
    )
