from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

class NafisPatient(models.Model):
    _name = 'nafis.patient'
    _description = 'Patient Record for Nafis Integration'

    name = fields.Char(string="Patient Name", required=True)
    national_id = fields.Char(string="National ID", required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], required=True)
    birth_date = fields.Date(string="Birth Date")
    visit_date = fields.Date(string="Visit Date", default=fields.Date.today)
    nafis_response = fields.Text(string="Nafis Response")
    fhir_payload_preview = fields.Text(string="FHIR Preview", readonly=True)

    def get_nafis_token(self):
        config = self.env['nafis.config'].search([], limit=1)
        if not config:
            raise Exception("No Nafis Configuration found")

        if config.test_mode:
            _logger.info("Test mode enabled: returning dummy token")
            return "dummy_test_token"

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            'grant_type': 'client_credentials',
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'scope': config.scopes or ''
        }
        try:
            response = requests.post(config.token_url, data=data, headers=headers)
            response.raise_for_status()
            token = response.json().get("access_token")
            if not token:
                raise Exception("Token not found in response")
            return token
        except Exception as e:
            _logger.error("Failed to get Nafis token: %s", e)
            raise

    def generate_fhir_payload(self):
        return {
            "resourceType": "Patient",
            "identifier": [{"system": "national-id", "value": self.national_id}],
            "name": [{"text": self.name}],
            "gender": self.gender,
            "birthDate": str(self.birth_date) if self.birth_date else None
        }

    def action_preview_fhir(self):
        for rec in self:
            try:
                preview = rec.generate_fhir_payload()
                rec.fhir_payload_preview = str(preview)
            except Exception as e:
                rec.fhir_payload_preview = f"Error: {str(e)}"

    def send_to_nafis(self):
        for rec in self:
            try:
                token = self.get_nafis_token()
                payload = rec.generate_fhir_payload()
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                config = self.env['nafis.config'].search([], limit=1)
                url = config.base_url.strip() if config and config.base_url else "https://httpbin.org/post"
                response = requests.post(url, headers=headers, json=payload)
                rec.nafis_response = f"Status: {response.status_code}\n{response.text}"
                _logger.info("Nafis Response [%s]: %s", response.status_code, response.text)
            except Exception as e:
                rec.nafis_response = str(e)
                _logger.error("Error sending to Nafis: %s", e)

    def test_nafis_token(self):
        for rec in self:
            try:
                token = self.get_nafis_token()
                rec.nafis_response = f"Test token retrieved: {token}"
            except Exception as e:
                rec.nafis_response = f"Token retrieval failed: {str(e)}"
