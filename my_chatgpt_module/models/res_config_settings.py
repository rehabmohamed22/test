from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    openapi_api_key = fields.Char(string="API Key", help="Provide the API key here", config_parameter="my_chatgpt_module.openapi_api_key", required=True)
