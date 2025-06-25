# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CustomerCreateTicket(http.Controller):

    @http.route('/bsma/create_ticket', type='json', auth="public", methods=['POST'])
    def create_credit_note(self, **kw):
        """
        JSON Request:
        {
            "params": {
                "project_code": "1"
            }
        }
        """
        if not kw:
            return {'status_code': 400, 'is_error': True, 'message': 'Bad request', 'result_rpo': ''}

        invoice_id = kw.get('invoice_id')
        if not invoice_id:
            return {'status_code': 400, 'is_error': True, "message": "Please add invoice_id", 'result_rpo': ''}

        invoice = request.env['account.move'].sudo().browse(int(invoice_id))

        if not invoice.exists():
            return {'status_code': 404, 'is_error': True, "message": "Invoice not found", 'result_rpo': ''}

        # Find the correct journal for credit notes (out_refund)
        # refund_journal = request.env['account.journal'].sudo().search([
        #     ('type', '=', 'sale'),
        #     ('refund_sequence', '=', True)
        # ], limit=1)

        # if not refund_journal:
        #     return {'status_code': 500, 'is_error': True, "message": "No valid refund journal found", 'result_rpo': ''}

        # Create credit note in the correct journal
        invoice._reverse_moves()

        # Extract the new credit note
        new_credit_note = request.env['account.move'].sudo().search([
            ('reversed_entry_id', '=', invoice.id), ('move_type', '=', 'out_refund')
        ], order="id desc", limit=1)  # Get the latest created credit note

        if not new_credit_note:
            return {'status_code': 500, 'is_error': True, "message": "Failed to create credit note", 'result_rpo': ''}

        # Post the credit note
        new_credit_note.action_post()

        return {
            'status_code': 200,
            'is_error': False,
            'message': 'Credit note created successfully',
            'result_rpo': {
                'credit_note_id': new_credit_note.id,
                'credit_note_number': new_credit_note.name
            }
        }