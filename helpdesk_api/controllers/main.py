from odoo import http
from odoo.http import request

class HelpdeskAPIController(http.Controller):

    @http.route('/api/update_ticket_status', type='json', auth='public', methods=['PUT'], csrf=False)
    def update_ticket_status(self, **kwargs):
        ticket_code = kwargs.get('ticket_code')
        new_status = kwargs.get('new_status')

        if not ticket_code or not new_status:
            return {'status': 'error', 'message': 'Missing ticket_code or new_status'}

        ticket = request.env['helpdesk.ticket'].sudo().search([('name', '=', ticket_code)], limit=1)
        if not ticket:
            return {'status': 'error', 'message': 'Ticket not found'}

        stage = request.env['helpdesk.stage'].sudo().search([('name', 'ilike', new_status)], limit=1)
        if not stage:
            return {'status': 'error', 'message': 'Invalid status'}

        ticket.stage_id = stage.id

        return {
            'status': 'success',
            'message': f'Ticket {ticket.name} moved to {stage.name}'
        }

    # @http.route('/api/test_input', type='json', auth='public', methods=['POST'], csrf=False)
    # def test_input(self, **kwargs):
    #     return {
    #         "ticket_code": kwargs.get('ticket_code'),
    #         "new_status": kwargs.get('new_status')
    #     }