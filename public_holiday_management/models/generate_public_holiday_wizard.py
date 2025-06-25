from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class GeneratePublicHolidaysWizard(models.TransientModel):
    _name = 'generate.public.holiday.wizard'
    _description = 'Generate Public Holidays by Year and Country'

    year = fields.Integer(string="Year", required=True, default=lambda self: date.today().year)
    country_id = fields.Many2one('res.country', string="Country", required=True)

    def action_generate(self):
        holidays = []

        if self.country_id.code == 'EG':
            holidays = [
                ("New Year's Day", date(self.year, 1, 1)),
                ("Revolution Day", date(self.year, 1, 25)),
                ("Sinai Liberation Day", date(self.year, 4, 25)),
                ("Labour Day", date(self.year, 5, 1)),
                ("Revolution Day", date(self.year, 7, 23)),
                ("Armed Forces Day", date(self.year, 10, 6)),
            ]
        elif self.country_id.code == 'SA':
            holidays = [
                ("Saudi National Day", date(self.year, 9, 23)),
                ("Eid al-Fitr", date(self.year, 4, 21)),
                ("Eid al-Adha", date(self.year, 6, 28)),
            ]
        else:
            raise UserError(_("No holiday template available for this country."))

        for name, day in holidays:
            self.env['public.holiday'].create({
                'name': name,
                'date': day,
                'company_id': self.env.company.id,
            })
