# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    employee_id = fields.Many2one('hr.employee',related='partner_id.employee_id')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    employee_id = fields.Many2one('hr.employee',related='partner_id.employee_id')

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    employee_id = fields.Many2one('hr.employee', string='Employee')

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    employee_id = fields.Many2one('hr.employee', string="Employee")
