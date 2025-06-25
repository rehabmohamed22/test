
#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(index=True, default_export_compatible=True)
    building_no = fields.Char(string="Building no", help="Building No")
    ar_building_no = fields.Char(string="Ar Building no", help="Arabic Building No")
    ar_district = fields.Char(string="Ar District", help="Arabic District")
    district = fields.Char(string="District", help="District")
    ar_code = fields.Char(string="En Code", help="English Code")
    code = fields.Char(string="Code", help="Code")
    ar_additional_no = fields.Char(string="En Additional no", help="Arabic Additional No")
    additional_no = fields.Char(string="Additional no", help="Additional No")
    ar_other_id = fields.Char(string="En Other ID", help="English Other ID")
    other_id = fields.Char(string="Other ID", help="Other ID")
    ar_name = fields.Char(string="Arabic Name")
    ar_street = fields.Char(string="English Street")
    ar_city = fields.Char(string="English City")
    ar_country_id = fields.Many2one('res.country',string="English Country")
    ar_zip = fields.Char(string="English Zip Code")
    ar_vat = fields.Char(string="English Vat")
    contract_value = fields.Float(string="Contract Value")

    @api.depends('name', 'ar_name')
    def _compute_display_name(self):
        for record in self:
            if record.ar_name and not record.name:
                record.display_name = record.ar_name
            elif record.name and not record.ar_name:
                record.display_name = record.name
            elif record.name and record.ar_name:
                record.display_name = f"{record.name} - {record.ar_name}"
            else:
                record.display_name = "Unnamed Partner"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None,order=None):
        args = args or []
        domain = []
        if name:
            domain = ['|','|', ('name', operator, name), ('ar_name', operator, name),('ref', operator, name)]
        return self._search(domain+args,limit=limit,access_rights_uid=name_get_uid,order=order)


    # is_customer = fields.Boolean(help="Customers")
    # is_vendor = fields.Boolean(help="Vendors")

    # @api.model
    # def create(self, vals_list):
    #     result = super(Partner, self).create(vals_list)
    #     if result.customer_rank == 1:
    #         result.is_customer = True
    #     elif result.supplier_rank == 1:
    #         result.is_vendor = True
    #     return result
