from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)


class ZidOAuthController(http.Controller):

    @http.route('/zid/authorize', type='http', auth='user')
    def zid_redirect(self, **kwargs):
        config = request.env['zid.settings'].sudo().search([], limit=1)
        redirect_uri = 'https://4583-154-236-119-130.ngrok-free.app/zid/callback'
        url = (
            f"https://oauth.zid.sa/oauth/authorize?client_id={config.client_id}"
            f"&redirect_uri={redirect_uri}&response_type=code"
        )
        _logger.info("sssssssssss %s", config.client_id)
        return request.redirect(url)

    @http.route('/zid/callback', type='http', auth='public', csrf=False)
    def zid_callback(self, **kwargs):
        code = kwargs.get('code')
        if not code:
            return "<h1>فشل الربط: الكود غير موجود</h1>"

        _logger.info("ZID CALLBACK STARTED")
        _logger.info("Request KWARGS: %s", kwargs)

        config = request.env['zid.settings'].sudo().search([], limit=1)
        if not config:
            return "<h1>فشل الربط: إعدادات زد غير موجودة</h1>"

        redirect_uri = 'https://4583-154-236-119-130.ngrok-free.app/zid/callback'

        payload = {
            'grant_type': 'authorization_code',
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'redirect_uri': redirect_uri,
            'code': code,
        }

        response = requests.post("https://oauth.zid.sa/oauth/token", data=payload)
        data = response.json()

        _logger.info("Zid response: %s", data)

        if 'access_token' in data:
            config.sudo().write({
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'authorization': data.get('authorization')
            })
            return "<h1>تم الربط بنجاح!</h1>"
        else:
            return f"<h1>فشل الربط: {data}</h1>"

