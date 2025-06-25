from odoo import models, fields
from odoo.exceptions import ValidationError
import base64
import xlrd

class InstallmentsImportWizard(models.TransientModel):
    _name = 'installments.import.wizard'
    _description = 'Import Installments from Excel'

    file = fields.Binary(string="Excel File", required=True)

    def import_excel(self):
        try:
            data = base64.b64decode(self.file)
            book = xlrd.open_workbook(file_contents=data)
            sheet = book.sheet_by_index(0)

            for row in range(1, sheet.nrows):
                external_id_raw = sheet.cell(row, 0).value
                external_id = str(external_id_raw).strip()
                amount = float(sheet.cell(row, 2).value)

                if '.' not in external_id:
                    raise ValidationError(f"Invalid External ID at row {row + 1}: {external_id}")

                module, xml_id = external_id.split('.')
                record = self.env.ref(f"{module}.{xml_id}", raise_if_not_found=False)

                if record and record._name == 'installments.board':
                    if record.paid_amount == 0:
                        record.amount = amount
        except Exception as e:
            raise ValidationError(f"Failed to import file: {str(e)}")
