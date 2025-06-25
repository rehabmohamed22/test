from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.populate import compute


class Property(models.Model):
    _name = 'property'
    _description = 'Property'
    _inherit = ['mail.thread' , 'mail.activity.mixin']

    name = fields.Char(required=True, size=100, default='New')
    ref = fields.Char(default='New' , readonly=1)

    description = fields.Text(tracking=1)
    postcode = fields.Char()
    expected_sailing_date = fields.Date(tracking=1)
    date_availability = fields.Date(tracking=1)
    is_late = fields.Boolean()
    expected_price = fields.Float()
    sailing_price = fields.Float()
    bedrooms = fields.Integer()
    living_area = fields.Float()
    diff =fields.Float(compute='_compute_diff' , store =1)
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Float()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('west', 'West'),
        ('east', 'East'),
        ('south', 'South'),
    ])
    active =fields.Boolean(default=True)
    owner_address = fields.Char(related='owner_id.address' , readonly=0, store=1)
    owner_phone = fields.Char(related='owner_id.phone' ,readonly=0, store=1)
    line_ids = fields.One2many('property.line','property_id')

    # Database-level constraint for unique name
    _sql_constraints = [('name_unique', 'unique("name")', 'State name already exists')]

    owner_id = fields.Many2one('owner')
    tags_ids = fields.Many2many('tags')
    state = fields.Selection([
        ('draft','Draft'),
        ('pending','Pending'),
        ('sold','sold'),
        ('closed', 'Closed'),

    ] , default='draft')


    @api.constrains('bedrooms')
    def _check_bedrooms_greater_zero(self):
        for rec in self:
            if rec.bedrooms <= 0:
                raise ValidationError('The number of bedrooms must be a positive integer greater than zero.')

    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state, 'draft', 'Moved to draft')
            rec.state = 'draft'

    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending', 'Moved to pending')
            rec.state = 'pending'

    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold', 'Property sold')
            rec.state = 'sold'

    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed', 'Property closed')
            rec.state = 'closed'

    @api.depends('expected_price' , 'sailing_price' , 'owner_id.phone')
    def _compute_diff(self):
        for rec in self:
            rec.diff= rec.expected_price - rec.sailing_price
    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        return {
            'warning' : {'title' : 'warning' , 'message' : 'negative value .' , 'type' : 'notification'}
        }
    # @api.model_create_multi
    # def create(self, vals):
    #     res = super(Property,self).create(vals)
    #     print("Inside create Method")
    #
    #     return res


    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        res = super(Property,self)._search(domain, offset=0, limit=None, order=None, access_rights_uid=None)
        print("inside Search method")
        return res

    def write(self, vals):
        res = super(Property,self).write(vals)
        print("inside write method")
        return res

    def unlink(self):
        res = super(Property,self).unlink()
        print("inside unlink method")
        return res
    def check_expected_sailing_date(self):
            property_ids = self.search([])
            for rec in property_ids:
              if rec.expected_sailing_date and rec.expected_sailing_date < fields.date.today():
                 rec.is_late=True

    @api.model
    def create(self, vals):
         res = super(Property,self).create(vals)
         if res.ref == "New" :
            res.ref = self.env['ir.sequence'].next_by_code('property_seq')
         return res
    def create_history_record(self, old_state,new_state,reason):
        for rec in self:
            rec.env['property.history'].create({
                'user_id': rec.env.uid,
                'property_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or ""

            })

    def action_open_change_state_wizard(self):
        action= self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context'] = {'default_property_id' : self.id}
        return action

class PropertyLine(models.Model):
    _name = 'property.line'

    area = fields.Float()
    description = fields.Char()
    property_id= fields.Many2one('property')
