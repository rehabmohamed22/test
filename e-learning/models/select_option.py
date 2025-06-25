from odoo import models, fields, api

class ProgrammingLanguage(models.Model):
    _name = 'programming.language'
    _description = 'Programming Language'

    name = fields.Char(string="Language Name", required=True)

    @api.model
    def _initialize_default_languages(self):
        default_languages = ['Scratch', 'Python', 'C++']
        existing_languages = self.search([]).mapped('name')
        for language in default_languages:
            if language not in existing_languages:
                self.create({'name': language})

    def init(self):
        self._initialize_default_languages()

class LeadSource(models.Model):
    _name = 'lead.source'
    _description = 'Lead Source'

    name = fields.Char(string="Lead Source", required=True)

    @api.model
    def _initialize_default_sources(self):
        default_sources = ['Website', 'Facebook', 'Instagram', 'Referral']
        existing_sources = self.search([]).mapped('name')
        for source in default_sources:
            if source not in existing_sources:
                self.create({'name': source})

    def init(self):
        self._initialize_default_sources()
