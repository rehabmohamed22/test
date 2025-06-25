from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.tools import Markup
import logging

_logger = logging.getLogger(__name__)

class CustomLogin(AuthSignupHome):

    @http.route('/web/login', type='http', auth="public", website=True, csrf=False)
    def web_login(self, redirect=None, **kw):
        response = super(CustomLogin, self).web_login(redirect=redirect, **kw)

        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            if user and user.id != 1:
                channel_name = f"ChatGPT - {user.name}"
                channel = request.env['discuss.channel'].sudo().search([('name', '=', channel_name)], limit=1)
                if not channel:
                    channel = request.env['discuss.channel'].sudo().create({
                        'name': channel_name,
                        'channel_type': 'chat',
                        'channel_partner_ids': [(4, user.partner_id.id)],
                    })
                    _logger.info("تم إنشاء قناة خاصة للمستخدم: %s", channel_name)

                welcome_msg = """
                <h3>مرحباً بك!</h3>
                <p>أنا مساعد ذكي يمكنني مساعدتك في تنفيذ الاستعلامات وتحليل البيانات وإنشاء التقارير.</p>
                <p>كيف يمكنني مساعدتك اليوم؟</p>
                """


                chatbot_user = request.env.ref('my_chatgpt_module.user_chatgpt_module')
                channel.with_user(chatbot_user).with_context(skip_chatgpt=True).message_post(
                    body=Markup(welcome_msg),
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                )
                _logger.info("تم إرسال الرسالة الترحيبية للمستخدم: %s في القناة %s", user.name, channel.name)
        return response
