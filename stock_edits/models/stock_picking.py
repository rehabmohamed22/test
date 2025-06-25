from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking Inherit"

    partner_ref = fields.Char(
        related="partner_id.ref",
        store=1
    )
    receipt_number = fields.Char()
    has_validate_group = fields.Boolean(
        compute="_compute_has_validate_group"
    )
    employee_id = fields.Many2one(
        'hr.employee'
    )
    project_name_id = fields.Many2one(
        'res.project',related='partner_id.project_id',store=True,
        string="Projects",
        help="Select both Arabic and English projects."
    )




    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id:
    #         self.project_name_id=self.partner_id.project_id.id
    def send_mail(self):
        self.env.ref('stock_edits.mail_template_data_delivery').send_mail(
            self.id, force_send=True
        )
    def _compute_has_validate_group(self):
        for rec in self:
            if rec.picking_type_code != 'outgoing':
                rec.has_validate_group = True
            elif (self.env.user.has_group('stock_edits.group_picking_validate')
                and rec.picking_type_code == 'outgoing'):
                rec.has_validate_group = True
            else:
                rec.has_validate_group = False

    def button_validate(self):

        """ Override button_validate """
        for line in self.move_ids_without_package:
            line.check_on_hand_quantity()

        res = super(StockPicking, self).button_validate()
        if not self.employee_id:
            raise ValidationError(_('You must select an employee for this picking.'))

        for rec in self:
            if rec.picking_type_code == 'incoming':
                if not rec.receipt_number:
                    raise ValidationError(_("You must enter a receipt number"))
                else:
                    existing_picking = self.env['stock.picking'].sudo().search([
                        ('receipt_number', '=', rec.receipt_number),
                        ('id', '!=', rec.id),
                        ('state', '=', 'done')
                    ])
                    if existing_picking:
                        raise ValidationError("This receipt number is already exist.")
            if rec.picking_type_code in ['outgoing', 'internal']:
                for move in rec.move_ids_without_package:
                    if move.quantity > move.on_hand_quantity:
                        print(move.quantity)
                        print(move.on_hand_quantity)
                        raise ValidationError(_("Quantity must be lower than or equal on hand quantity"))
        if self.picking_type_code == 'outgoing':
            self.send_mail()
        return res

    def copy(self, default=None):
        for line in self.move_ids_without_package:
            line.check_on_hand_quantity()
        res = super(StockPicking, self).copy(default)
        return res

    def check_on_hand(self):
        for line in self.move_ids_without_package:
            line.check_on_hand_quantity()