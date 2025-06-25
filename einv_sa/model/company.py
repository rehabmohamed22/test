#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    building_no = fields.Char(string="Building no", help="Building No")
    ar_building_no = fields.Char(string="En Building no", help="English Building No")
    ar_district = fields.Char(string="En District", help="Arabic District")
    district = fields.Char(string="District", help="District")
    ar_code = fields.Char(string="En Code", help="English Code")
    code = fields.Char(string="Code", help="Code")
    ar_additional_no = fields.Char(string="En Additional no", help="English Additional No")
    additional_no = fields.Char(string="Additional no", help="Additional No")
    ar_other_id = fields.Char(string="Ar Other ID", help="Arabic Other ID")
    other_id = fields.Char(string="Other ID", help="Other ID")
    ar_name = fields.Char(string="Arabic Name")
    ar_street = fields.Char(string="English Street")
    ar_city = fields.Char(string="English City")
    ar_country_id = fields.Many2one('res.country', string="English Country")
    ar_zip = fields.Char(string="English Zip Code")
    ar_vat = fields.Char(string="English Vat")
    stamp = fields.Binary()
    signature = fields.Binary()
    account_num = fields.Char(string="Account Number")
    bank = fields.Char()
    iban = fields.Char()