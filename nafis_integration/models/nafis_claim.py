from odoo import models, fields
import requests
import xlsxwriter
import base64
import io
import json

class NafisClaim(models.Model):
    _name = 'nafis.claim'
    _description = 'Claim Record for Nafis Integration'

    patient_id = fields.Many2one('nafis.patient', string="Patient", required=True)
    encounter_id = fields.Many2one('nafis.encounter', string="Encounter")
    insurer = fields.Char(string="Insurer")
    amount = fields.Float(string="Claimed Amount")
    diagnosis = fields.Text(string="Diagnosis")
    procedure = fields.Text(string="Procedure")
    nafis_response = fields.Text(string="Nafis Response")
    fhir_payload_preview = fields.Text(string="FHIR Preview", readonly=True)
    create_date = fields.Datetime(string="Created At", readonly=True)
    claim_response_ids = fields.One2many('nafis.claim.response', 'claim_id', string="Claim Responses")

    def generate_fhir_payload(self):
        return {
            "resourceType": "Claim",
            "status": "active",
            "type": {"coding": [{"code": "professional"}]},
            "use": "claim",
            "patient": {
                "reference": f"Patient/{self.patient_id.id}"
            },
            **({"insurer": {"display": self.insurer}} if self.insurer else {}),
            "item": [{
                "sequence": 1,
                **({"diagnosisCodeableConcept": {"text": self.diagnosis}} if self.diagnosis else {}),
                **({"procedure": [{"sequence": 1, "procedureCodeableConcept": {"text": self.procedure}}]} if self.procedure else {}),
                "unitPrice": {"value": self.amount, "currency": "SAR"}
            }]
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

                token = "dummy_test_token" if config.test_mode else self.env['nafis.patient'].get_nafis_token()
                payload = rec.generate_fhir_payload()
                url = config.base_url.strip() if config.base_url else "https://httpbin.org/post"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                response = requests.post(url, headers=headers, json=payload)
                rec.nafis_response = f"Status: {response.status_code}\n{response.text}"
                try:
                    response_data = response.json()
                    rec.env['nafis.claim.response'].create({
                        'claim_id': rec.id,
                        'status': response_data.get('status', 'unknown'),
                        'message': response_data.get('message', ''),
                        'approved_amount': response_data.get('amount', 0.0),
                        'full_response': json.dumps(response_data)
                    })
                except Exception:
                    pass
            except Exception as e:
                rec.nafis_response = f"Error: {str(e)}"

    def action_export_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Claims")

        headers = ["Patient", "Encounter", "Insurer", "Claimed Amount", "Diagnosis", "Procedure", "Created At"]
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        for row, rec in enumerate(self, start=1):
            sheet.write(row, 0, rec.patient_id.name)
            sheet.write(row, 1, rec.encounter_id.display_name or '')
            sheet.write(row, 2, rec.insurer or '')
            sheet.write(row, 3, rec.amount)
            sheet.write(row, 4, rec.diagnosis or '')
            sheet.write(row, 5, rec.procedure or '')
            sheet.write(row, 6, str(rec.create_date) or '')

        workbook.close()
        output.seek(0)
        attachment = rec.env['ir.attachment'].create({
            'name': 'nafis_claims_export.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'nafis.claim',
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }