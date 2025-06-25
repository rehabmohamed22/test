from odoo import models, fields
from datetime import datetime
import requests
import logging

_logger = logging.getLogger(__name__)

class NafisEncounter(models.Model):
    _name = 'nafis.encounter'
    _description = 'Encounter Record for Nafis Integration'

    patient_id = fields.Many2one('nafis.patient', string="Patient", required=True)
    encounter_type = fields.Selection([
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient'),
        ('emergency', 'Emergency')
    ], string="Encounter Type", required=True)
    reason = fields.Char(string="Reason")
    start_date = fields.Datetime(string="Start Time", required=True)
    end_date = fields.Datetime(string="End Time")
    nafis_response = fields.Text(string="Nafis Response")
    fhir_payload_preview = fields.Text(string="FHIR Preview", readonly=True)

    def generate_fhir_payload(self):
        return {
            "resourceType": "Encounter",
            "status": "finished" if self.end_date else "in-progress",
            "class": {
                "code": self.encounter_type
            },
            "subject": {
                "reference": f"Patient/{self.patient_id.id}",
                "display": self.patient_id.name
            },
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat() if self.end_date else None
            },
            "reasonCode": [{"text": self.reason}] if self.reason else []

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
                config = rec.env['nafis.config'].search([], limit=1)
                if not config:
                    raise Exception("Nafis Configuration not found.")

                if config.test_mode:
                    token = "dummy_test_token"
                else:
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    data = {
                        'grant_type': 'client_credentials',
                        'client_id': config.client_id,
                        'client_secret': config.client_secret,
                        'scope': config.scopes or ''
                    }
                    resp = requests.post(config.token_url, data=data, headers=headers)
                    resp.raise_for_status()
                    token = resp.json().get("access_token")

                payload = rec.generate_fhir_payload()

                url = config.base_url.strip() if config.base_url else "https://httpbin.org/post"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                response = requests.post(url, headers=headers, json=payload)

                rec.nafis_response = f"Status: {response.status_code}\n{response.text}"
                _logger.info("Nafis Encounter Sent [%s]: %s", response.status_code, response.text)

            except Exception as e:
                rec.nafis_response = f"Error: {str(e)}"
                _logger.error("Send to Nafis Failed: %s", e)
