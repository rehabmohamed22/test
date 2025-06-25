from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Res Partner Inherit"

    employee = fields.Boolean()

    @api.constrains('ref', 'company_id')
    def _check_unique_ref_per_company(self):
        for partner in self:
            if partner.ref:
                existing_partner = self.env['res.partner'].sudo().search([
                    ('ref', '=', partner.ref),
                    '|', ('company_id', '=', partner.company_id.id), ('company_id', '=', False),
                    ('id', '!=', partner.id)
                ])
                if existing_partner:
                    raise ValidationError("Reference must be unique per partner.")
