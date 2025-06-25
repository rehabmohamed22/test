# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    member_ids = fields.Many2many(
        'res.users', string='Salespersons',
        domain="[('company_ids', 'in', member_company_ids)]",
        compute='_compute_member_ids', inverse='_inverse_member_ids', search='_search_member_ids',
        help="Users assigned to this team.")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        compute='_compute_user_id',
        store=True, readonly=False, precompute=True, index=True,
        tracking=2,
        domain=lambda self: "[('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ))

class ResPartner(models.Model):
    _inherit = 'res.partner'
