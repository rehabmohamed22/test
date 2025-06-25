# from odoo import models, api
# import logging
# _logger = logging.getLogger(__name__)
# class ResUsers(models.Model):
#     _inherit = 'res.users'
#
#     @api.model
#     def create(self, vals):
#         user = super(ResUsers, self).create(vals)
#
#         channel_name = f"ChatGPT - {user.name}"
#         channel_exists = self.env['discuss.channel'].sudo().search([('name', '=', channel_name)], limit=1)
#         if not channel_exists:
#             self.env['discuss.channel'].sudo().create({
#                 'name': channel_name,
#                 'channel_type': 'chat',
#                 'public': 'private',
#                 'channel_partner_ids': [(6, 0, [user.partner_id.id])]
#             })
#             _logger.warning(f"🆕 Created private channel for new user: {channel_name}")
#
#         return user
#

# from odoo import models, api
# from odoo.tools import logging
# import tempfile
# import base64
# import whisper
#
# _logger = logging.getLogger(__name__)
#
#
# class MailMessage(models.Model):
#     _inherit = 'mail.message'
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         messages = super().create(vals_list)
#
#         for message in messages:
#             try:
#                 attachments = message.attachment_ids
#                 for attachment in attachments:
#                     if attachment.mimetype and 'audio' in attachment.mimetype:
#                         try:
#                             _logger.warning("صوت مرفق: %s (%s)", attachment.name, attachment.mimetype)
#
#                             with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#                                 tmp.write(base64.b64decode(attachment.datas))
#                                 path = tmp.name
#
#                             model = whisper.load_model("base")
#                             audio = whisper.load_audio(path)
#                             audio = whisper.pad_or_trim(audio)
#                             mel = whisper.log_mel_spectrogram(audio).to(model.device)
#                             _, probs = model.detect_language(mel)
#                             lang = max(probs, key=probs.get)
#                             result = whisper.decode(model, mel, whisper.DecodingOptions(language=lang, fp16=False))
#
#                             transcribed_text = result.text
#                             _logger.warning("تم تحويل الصوت إلى: %s", transcribed_text)
#
#                             if message.model == 'discuss.channel' and message.res_id:
#                                 channel = self.env['discuss.channel'].browse(message.res_id)
#                                 channel.with_context(skip_chatgpt=False)._notify_thread(
#                                     message, msg_vals={'body': transcribed_text})
#
#                             break  # break from attachment loop
#                         except Exception as e:
#                             _logger.error("❌ فشل تحويل الصوت: %s", e)
#             except Exception as outer_e:
#                 _logger.error("❌ مشكلة غير متوقعة في mail.message.create: %s", outer_e)
#
#         return messages



# import gspread
# from google.oauth2.service_account import Credentials
#
# # مسار ملف JSON
# SERVICE_ACCOUNT_FILE = 'my_chatgpt_module/robotic-epoch-454010-i1-1870b647f5d0.json'
#
# # إعداد الصلاحيات
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
#           'https://www.googleapis.com/auth/drive']
#
# credentials = Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#
# # الاتصال بـ Google Sheets
# client = gspread.authorize(credentials)
#
# # فتح الملف باستخدام ID الخاص بـ Google Sheets
# sheet = client.open_by_key('1YkizrIlhV5hgciEhL9QFG3Jnug3H7D2l_VuXOKuDIhk')
#
# # اختيار الورقة الأولى
# worksheet = sheet.sheet1
#
# # إضافة بيانات تجريبية
# worksheet.append_row(['Test Question', 'Test Answer', 'Test Tokens'])
#
# print("✅ تم إضافة الصف التجريبي إلى Google Sheets بنجاح.")
#

# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.linear_model import LogisticRegression
# import pickle
#
# import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('punkt_tab')
#
# arabic_stopwords = set(stopwords.words('arabic'))
#
# def extract_important_words(text):
#     tokens = word_tokenize(text)
#     important_words = [word for word in tokens if word not in arabic_stopwords]
#     return important_words
#
# def train_model_classifier(training_data, labels):
#     vectorizer = CountVectorizer()
#     X = vectorizer.fit_transform(training_data)
#     clf = LogisticRegression()
#     clf.fit(X, labels)
#     with open("vectorizer.pkl", "wb") as f:
#         pickle.dump(vectorizer, f)
#     with open("classifier.pkl", "wb") as f:
#         pickle.dump(clf, f)
#     return vectorizer, clf
#
# def predict_model(text, vectorizer, clf):
#     X = vectorizer.transform([text])
#     predicted_model = clf.predict(X)
#     return predicted_model[0]
#
# question = "اريد معرفة تفاصيل شريك جديد في النظام"
# important_words = extract_important_words(question)
# print("الكلمات الهامة:", important_words)
#
# training_data = ["تفاصيل شريك", "طلب فاتورة", "تفاصيل طلب مبيعات"]
# labels = ["res.partner", "account.invoice", "sale.order"]
# vectorizer, clf = train_model_classifier(training_data, labels)
# predicted_model = predict_model(" ".join(important_words), vectorizer, clf)
# print("الموديل المتنبأ به:", predicted_model)
