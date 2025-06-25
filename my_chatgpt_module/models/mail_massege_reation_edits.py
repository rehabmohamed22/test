# import os
# import uuid
# import json
# from datetime import datetime
# import gspread
# from google.oauth2.service_account import Credentials
# from odoo import models, api, fields
# from odoo.tools import Markup
#
# class ChatGPTModuleChannel(models.Model):
#     _inherit = 'discuss.channel'
#
#     def _notify_thread(self, message, msg_vals=False, **kwargs):
#         print("📌 _notify_thread called")
#         if self.env.context.get('skip_chatgpt'):
#             print("⏭️ Skipping ChatGPT processing due to context flag")
#             return super(ChatGPTModuleChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
#
#         body = msg_vals.get('body', '')
#         if not body:
#             return super(ChatGPTModuleChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
#
#         res = super(ChatGPTModuleChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
#         print("✅ Super _notify_thread completed")
#         self.env.cr.commit()
#
#         # Ensure private user channel exists or create one
#         current_user = self.env.user
#         channel_name = f"ChatGPT - {current_user.name}"
#         user_channel = self.env['discuss.channel'].sudo().search([('name', '=', channel_name)], limit=1)
#
#         if not user_channel:
#             user_channel = self.env['discuss.channel'].sudo().create({
#                 'name': channel_name,
#                 'channel_type': 'chat',
#                 'public': 'private',
#                 'channel_partner_ids': [(6, 0, [current_user.partner_id.id])]
#             })
#             print(f"🆕 Created private channel: {channel_name}")
#
#         # 1. Generate UUID
#         generated_uuid = str(uuid.uuid4())
#         print(f"🔑 Generated UUID: {generated_uuid}")
#
#         posted_message = None
#         row_number = 0
#
#         # 2. Create record in chatgpt.module with UUID and question
#         chatgpt_record = self.env['chatgpt.module'].create({
#             'question': body,
#             'uuid': generated_uuid,
#             'user_id': current_user.id,
#         })
#         print(f"📝 Created ChatGPTModule record ID: {chatgpt_record.id}")
#
#         # 3. Call compute_answer_action to generate the answer and capture extra data.
#         generated_data = chatgpt_record.compute_answer_action() or {}
#         answer = generated_data.get("answer", "No answer generated.")
#         models_list = generated_data.get("models", [])
#         tokens = generated_data.get("tokens", [])
#         sql_query = generated_data.get("sql_query", "")
#         rephrased_question = generated_data.get("rephrased_question", "")
#         result = generated_data.get("res", "")
#         if isinstance(result, list):
#             result = '\n'.join([
#                 json.dumps(row, ensure_ascii=False) if isinstance(row, dict) else str(row)
#                 for row in result
#             ])
#         else:
#             result = str(result)
#         print(f"💬 GPT Answer: {answer}")
#
#         # 4. Format the message with the answer
#         formatted_message = Markup(f"""
#             <div dir=\"auto\" data-uuid=\"{generated_uuid}\" style=\"
#                 background-color: #f0f8ff;
#                 padding: 10px;
#                 border-radius: 8px;
#                 line-height: 1.8;
#                 border: 1px solid #dce6f0;
#                 font-size: 15px;
#                 color: #333;
#                 margin: 5px 0;
#             \">
#                 • {answer.strip()}
#             </div>
#         """)
#
#         chatbot_user = self.env.ref('my_chatgpt_module.user_chatgpt_module')
#         posted_message = user_channel.with_user(chatbot_user).with_context(skip_chatgpt=True).message_post(
#             body=formatted_message,
#             message_type='comment',
#             subtype_xmlid='mail.mt_comment'
#         )
#         print(f"📨 Posted Discuss message ID: {posted_message.id}")
#
#         chatgpt_record.write({'message_id': posted_message.id})
#         self.env.cr.commit()
#         self.env.cr.flush()
#         print(f"📌 Updated ChatGPT record with message_id: {str(posted_message.id)}")
#
#         import time
#         time.sleep(1)
#
#         try:
#             module_path = os.path.dirname(os.path.abspath(__file__))
#             SERVICE_ACCOUNT_FILE = os.path.join(module_path, 'robotic-epoch-454010-i1-1870b647f5d0.json')
#             SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
#             credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#             client = gspread.authorize(credentials)
#             sheet = client.open_by_key('1YkizrIlhV5hgciEhL9QFG3Jnug3H7D2l_VuXOKuDIhk')
#             worksheet = sheet.sheet1
#
#             timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             new_row = [
#                 timestamp,
#                 ', '.join([str(m) for m in models_list]),
#                 ', '.join([str(t) for t in tokens]),
#                 body,
#                 rephrased_question,
#                 sql_query,
#                 str(posted_message.id),
#                 result
#             ]
#
#             worksheet.append_row(new_row, value_input_option='USER_ENTERED')
#             row_number = len(worksheet.get_all_values())
#             chatgpt_record.sheet_row_number = row_number
#             print(f"📄 Saved full data to sheet row {row_number} with UUID {generated_uuid} and message_id {posted_message.id}")
#         except Exception as e:
#             print(f"❌ Error writing to Google Sheet: {e}")
#
#         self.env.cr.commit()
#         return {'type': 'ir.actions.client', 'tag': 'web.action_reload'}
#
#
# class MailMessageReaction(models.Model):
#     _inherit = 'mail.message.reaction'
#
#     @api.model
#     def create(self, vals):
#         print("🔥 Reaction create triggered")
#
#         message_id = vals.get("message_id")
#         record = super().create(vals)
#
#         reaction = record.content
#         print(f"➡ message_id: {message_id}, reaction: {reaction}")
#         print(f"🧪 Comparing message_id: {message_id} (type: {type(message_id)})")
#
#         print(f"🧪 Searching for ChatGPT record with message_id: {message_id}")
#         chatgpt_record = self.env['chatgpt.module'].sudo().search([
#             ('message_id.id', '=', message_id)
#         ], limit=1)
#
#         try:
#             update_feedback_in_sheet_by_message_id(message_id, reaction)
#             chatgpt_record.feedback = reaction
#         except Exception as e:
#             print(f"❌ Error updating sheet: {e}")
#
#         return record
#
#
# def update_feedback_in_sheet_by_message_id(message_id, feedback_emoji):
#     module_path = os.path.dirname(os.path.abspath(__file__))
#     SERVICE_ACCOUNT_FILE = os.path.join(module_path, 'robotic-epoch-454010-i1-1870b647f5d0.json')
#     SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
#     credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     client = gspread.authorize(credentials)
#     sheet = client.open_by_key('1YkizrIlhV5hgciEhL9QFG3Jnug3H7D2l_VuXOKuDIhk')
#     worksheet = sheet.sheet1
#
#     all_rows = worksheet.get_all_values()
#     header = all_rows[0]
#
#     if "message_id" not in header or "feedback" not in header:
#         raise ValueError("Sheet must have 'message_id' and 'feedback' columns")
#
#     message_id_col = header.index("message_id")
#     feedback_col = header.index("feedback")
#
#     for row_index, row in enumerate(all_rows[1:], start=2):
#         if row[message_id_col] == str(message_id):
#             worksheet.update_cell(row_index, feedback_col + 1, feedback_emoji)
#             print(f"✅ Updated feedback for message_id {message_id} with {feedback_emoji}")
#             return
#
#     raise ValueError(f"message_id {message_id} not found in sheet")
#
# from odoo import models, api
# import base64
# import tempfile
# import whisper
# import logging
#
# _logger = logging.getLogger(__name__)
#
# class MailMessage(models.Model):
#     _inherit = 'mail.message'
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         messages = super().create(vals_list)
#
#         for message in messages:
#             attachments = message.attachment_ids
#             for attachment in attachments:
#                 if attachment.mimetype and 'audio' in attachment.mimetype:
#                     try:
#                         _logger.warning(f"🎧 صوت مرفق: {attachment.name} ({attachment.mimetype})")
#
#                         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#                             tmp.write(base64.b64decode(attachment.datas))
#                             path = tmp.name
#
#                         model = whisper.load_model("base")
#                         audio = whisper.load_audio(path)
#                         audio = whisper.pad_or_trim(audio)
#                         mel = whisper.log_mel_spectrogram(audio).to(model.device)
#                         _, probs = model.detect_language(mel)
#                         lang = max(probs, key=probs.get)
#                         result = whisper.decode(model, mel, whisper.DecodingOptions(language=lang, fp16=False))
#
#                         # ✅ ما تحطش النص كـ body عشان ما يظهرش في الشات
#                         transcribed_text = result.text
#                         _logger.warning(f"🖍️ تم تحويل الصوت إلى: {transcribed_text}")
#
#                         # ✅ نفذ _notify_thread مباشرة بالنص بدون عرضه
#                         if message.model == 'discuss.channel' and message.res_id:
#                             channel = self.env['discuss.channel'].browse(message.res_id)
#                             channel.with_context(skip_chatgpt=False)._notify_thread(
#                                 message, msg_vals={'body': transcribed_text})
#
#                         break
#                     except Exception as e:
#                         _logger.error(f"❌ فشل التحويل الصوتي: {e}")
#
#         return messages
#
#

import os

import gspread
from google.oauth2.service_account import Credentials

from odoo import models, api



class MailMessageReaction(models.Model):
    _inherit = 'mail.message.reaction'

    @api.model
    def create(self, vals):
        print("🔥 Reaction create triggered")

        message_id = vals.get("message_id")
        record = super().create(vals)

        reaction = record.content
        print(f"➡ message_id: {message_id}, reaction: {reaction}")
        print(f"🧪 Comparing message_id: {message_id} (type: {type(message_id)})")

        print(f"🧪 Searching for ChatGPT record with message_id: {message_id}")
        chatgpt_record = self.env['chatgpt.module'].sudo().search([
            ('message_id.id', '=', message_id)
        ], limit=1)

        try:
            update_feedback_in_sheet_by_message_id(message_id, reaction)
            chatgpt_record.feedback = reaction
        except Exception as e:
            print(f"❌ Error updating sheet: {e}")

        return record


def update_feedback_in_sheet_by_message_id(message_id, feedback_emoji):
    module_path = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(module_path, 'robotic-epoch-454010-i1-1870b647f5d0.json')
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key('1YkizrIlhV5hgciEhL9QFG3Jnug3H7D2l_VuXOKuDIhk')
    worksheet = sheet.sheet1

    all_rows = worksheet.get_all_values()
    header = all_rows[0]

    if "message_id" not in header or "feedback" not in header:
        raise ValueError("Sheet must have 'message_id' and 'feedback' columns")

    message_id_col = header.index("message_id")
    feedback_col = header.index("feedback")

    for row_index, row in enumerate(all_rows[1:], start=2):
        if row[message_id_col] == str(message_id):
            worksheet.update_cell(row_index, feedback_col + 1, feedback_emoji)
            print(f"✅ Updated feedback for message_id {message_id} with {feedback_emoji}")
            return

    raise ValueError(f"message_id {message_id} not found in sheet")



