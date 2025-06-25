import os
import uuid
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from odoo import models, api, fields
from odoo.tools import Markup
from odoo import models, api
import base64
import tempfile
import whisper
import logging

import json
import uuid
import threading
from datetime import datetime
from markupsafe import Markup
from odoo import models, api
from odoo.tools import logging
from google.oauth2.service_account import Credentials
import gspread
import os
import tempfile
import base64
import whisper

_logger = logging.getLogger(__name__)

import threading
from markupsafe import Markup


class ChatGPTModuleChannel(models.Model):
    _inherit = 'discuss.channel'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        print("📌 _notify_thread called")
        current_user = self.env.user
        channel_name = f"ChatGPT - {current_user.name}"
        user_channel = self.env['discuss.channel'].sudo().search([('name', '=', channel_name)], limit=1)
        if not user_channel:
            user_channel = self.env['discuss.channel'].sudo().create({
                'name': channel_name,
                'channel_type': 'chat',
                'channel_partner_ids': [(4, current_user.partner_id.id)]
            })
            print(f"🆕 Created private channel for user: {channel_name}")

        if self.env.context.get('skip_chatgpt'):
            print("⏭️ Skipping ChatGPT processing due to context flag")
            return super(ChatGPTModuleChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)

        body = msg_vals.get('body', '')
        attachments = message.attachment_ids

        for att in attachments:
            print(f"📎 Attachment: {att.name}, Mimetype: {att.mimetype}")

        is_voice_message = any(
            att.mimetype and att.mimetype.startswith('audio') for att in attachments
        )

        if not body and not is_voice_message:
            return super(ChatGPTModuleChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)

        if not is_voice_message:
            res = super(ChatGPTModuleChannel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
            print("✅ Super _notify_thread completed")
            self.env.cr.commit()


            generated_uuid = str(uuid.uuid4())
            print(f"🔑 Generated UUID: {generated_uuid}")

            posted_message = None
            row_number = 0

            chatgpt_record = self.env['chatgpt.module'].create({
                'question': body,
                'uuid': generated_uuid,
                'user_id': current_user.id,
            })
            self.env.cr.commit()

            print(f"📝 Created ChatGPTModule record ID: {chatgpt_record.id}")

            generated_data = chatgpt_record.compute_answer_action() or {}
            answer = generated_data.get("answer", "No answer generated.")
            models_list = generated_data.get("models", [])
            tokens = generated_data.get("tokens", [])
            sql_query = generated_data.get("sql_query", "")
            rephrased_question = generated_data.get("rephrased_question", "")
            result = generated_data.get("res", "")
            if isinstance(result, list):
                result = '\n'.join([
                    json.dumps(row, ensure_ascii=False) if isinstance(row, dict) else str(row)
                    for row in result
                ])
            else:
                result = str(result)
            print(f"💬 GPT Answer: {answer}")

            formatted_message = Markup(f"""
                <div dir="auto" data-uuid="{generated_uuid}" style="
                    background-color: #f0f8ff;
                    padding: 10px;
                    border-radius: 8px;
                    line-height: 1.8;
                    border: 1px solid #dce6f0;
                    font-size: 15px;
                    color: #333;
                    margin: 5px 0;
                ">
                    {answer.strip()}
                </div>
            """)

            chatbot_user = self.env.ref('my_chatgpt_module.user_chatgpt_module')
            posted_message = user_channel.with_user(chatbot_user).with_context(skip_chatgpt=True).message_post(
                body=formatted_message,
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )
            print(f"📨 Posted Discuss message ID: {posted_message.id}")


            self.env.cr.commit()
            self.env.cr.flush()
            print(f"📌 Updated ChatGPT record with message_id: {str(posted_message.id)}")

            import time
            time.sleep(1)

            try:
                module_path = os.path.dirname(os.path.abspath(__file__))
                SERVICE_ACCOUNT_FILE = os.path.join(module_path, 'robotic-epoch-454010-i1-1870b647f5d0.json')
                SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
                client = gspread.authorize(credentials)
                sheet = client.open_by_key('1YkizrIlhV5hgciEhL9QFG3Jnug3H7D2l_VuXOKuDIhk')
                worksheet = sheet.sheet1

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = [
                    timestamp,
                    ', '.join([str(m) for m in models_list]),
                    ', '.join([str(t) for t in tokens]),
                    body,
                    rephrased_question,
                    sql_query,
                    str(posted_message.id),
                    result
                ]
                worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                row_number = len(worksheet.get_all_values())
                chatgpt_record.sheet_row_number = row_number
                print(f"📄 Saved full data to sheet row {row_number} with UUID {generated_uuid} and message_id {posted_message.id}")
            except Exception as e:
                print(f"❌ Error writing to Google Sheet: {e}")

            self.env.cr.commit()
            return {'type': 'ir.actions.client', 'tag': 'web.action_reload'}

        else:
            print("🔊 Processing voice message separately")
            try:
                attachments = message.attachment_ids
                transcribed_text = ''
                for attachment in attachments:
                    if attachment.mimetype and attachment.mimetype.startswith('audio'):
                        try:
                            _logger.warning("🎤 صوت مرفق: %s (%s)", attachment.name, attachment.mimetype)

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                                tmp.write(base64.b64decode(attachment.datas))
                                path = tmp.name
                                _logger.warning("💾 تم حفظ الصوت مؤقتًا في: %s", path)

                            model = whisper.load_model("base")
                            audio = whisper.load_audio(path)
                            audio = whisper.pad_or_trim(audio)
                            mel = whisper.log_mel_spectrogram(audio).to(model.device)
                            _, probs = model.detect_language(mel)
                            lang = max(probs, key=probs.get)
                            options = whisper.DecodingOptions(language=lang, fp16=False, temperature=0.0)
                            result = whisper.decode(model, mel, options)

                            transcribed_text = result.text.strip()
                            _logger.warning("🗣️ تم تحويل الصوت إلى نص: %s", transcribed_text)
                            break
                        except Exception as e:
                            _logger.error("❌ فشل تحويل الصوت: %s", e)

                if not transcribed_text:
                    transcribed_text = "لم يتم تحويل الصوت إلى نص."

                generated_uuid = str(uuid.uuid4())

                chatgpt_record = self.env['chatgpt.module'].create({
                    'question': transcribed_text,
                    'uuid': generated_uuid,
                    'user_id': current_user.id,
                })

                self.env.cr.commit()
                generated_data = {}
                generated_data = chatgpt_record.compute_answer_action()

                try:
                    if not generated_data or "answer" not in generated_data:
                        raise Exception("No answer returned from compute_answer_action")
                except Exception as e:
                    _logger.error("❌ Error during compute_answer_action for voice: %s", e)
                    generated_data = {
                        "answer": f"❌ حصل خطأ أثناء المعالجة: {str(e)}",
                        "res": [],
                        "sql_query": "",
                        "tokens": [],
                        "rephrased_question": "",
                        "models": []
                    }

                answer = generated_data.get("answer", "No answer generated for voice message.")
                print(f"💬 Voice GPT Answer: {answer}")
                chatbot_user = self.env.ref('my_chatgpt_module.user_chatgpt_module')

                def post_voice_reply():
                    try:
                        with self.pool.cursor() as new_cr:
                            env = api.Environment(new_cr, self.env.uid, self.env.context)
                            formatted_message = Markup(f"""
                                <div dir="auto" data-uuid="{generated_uuid}" style="
                                    background-color: #f0f8ff;
                                    padding: 10px;
                                    border-radius: 8px;
                                    line-height: 1.8;
                                    border: 1px solid #dce6f0;
                                    font-size: 15px;
                                    color: #333;
                                    margin: 5px 0;
                                ">
                                    • {answer.strip()}
                                </div>
                            """)

                            posted_message = user_channel.with_env(env).with_user(chatbot_user).with_context(
                                skip_chatgpt=True).message_post(
                                body=formatted_message,
                                message_type='comment',
                                subtype_xmlid='mail.mt_comment'
                            )
                            _logger.warning("📨 Posted delayed GPT voice reply message ID: %s", posted_message.id)

                            import time
                            time.sleep(1)
                            try:
                                module_path = os.path.dirname(os.path.abspath(__file__))
                                SERVICE_ACCOUNT_FILE = os.path.join(module_path,
                                                                    'robotic-epoch-454010-i1-1870b647f5d0.json')
                                SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
                                          'https://www.googleapis.com/auth/drive']
                                credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
                                client = gspread.authorize(credentials)
                                sheet = client.open_by_key('1YkizrIlhV5hgciEhL9QFG3Jnug3H7D2l_VuXOKuDIhk')
                                worksheet = sheet.sheet1

                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                new_row = [
                                    timestamp,
                                    ', '.join([str(m) for m in generated_data.get("models", [])]),
                                    ', '.join([str(t) for t in generated_data.get("tokens", [])]),
                                    transcribed_text,
                                    generated_data.get("rephrased_question", ""),
                                    generated_data.get("sql_query", ""),
                                    str(posted_message.id),
                                    str(generated_data.get("res", ""))
                                ]
                                worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                                row_number = len(worksheet.get_all_values())
                                _logger.warning("📄 Saved voice data to sheet row %s with UUID %s and message_id %s",
                                                row_number, generated_uuid, posted_message.id)
                            except Exception as e:
                                _logger.error("❌ Error writing voice result to Google Sheet: %s", e)

                            new_cr.commit()
                    except Exception as e:
                        _logger.error("❌ Failed to post delayed GPT reply: %s", e)

                threading.Timer(1.0, post_voice_reply).start()

            except Exception as e:
                print(f"❌ Error processing voice message: {e}")
                self.env.cr.rollback()

            return {'type': 'ir.actions.client', 'tag': 'web.action_reload'}






