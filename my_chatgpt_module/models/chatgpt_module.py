# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
import re
from openai import OpenAI
import time
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import calendar
from odoo.tools import Markup

import re
from openai import OpenAI
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from odoo import models, fields, api
import os
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
import html


class ChatGPTModule(models.Model):
    _name = 'chatgpt.module'
    _description = 'ChatGPT Integration'

    question = fields.Text(string="Question", required=True)
    answer = fields.Text(string="Answer", readonly=True)
    sheet_row_number = fields.Integer(string="Google Sheet Row", readonly=True)
    message_id = fields.Many2one('mail.message', string="Message", ondelete='set null')
    feedback = fields.Char(string="Feedback", readonly=True)
    uuid = fields.Char(string="UUID", readonly=True)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.uid)

    def compute_answer_action(self):
        for record in self:
            if record.question:
                question_lang = self.detect_language(record.question)

                important_data = self.extract_important_words(record.question)
                extracted_rephrased_question = important_data.get("rephrased_question", record.question)
                extracted_tokens = important_data.get("filtered_tokens", [])
                extracted_potential_models = important_data.get("potential_models", [])
                question_type = important_data.get("question_type", "general")
                general_response = important_data.get("response", "")

                if question_type == "general":
                    record.answer = general_response
                    return {
                        "answer": record.answer,
                        "models": [],
                        "tokens": extracted_tokens,
                        "sql_query": "",
                        "rephrased_question": extracted_rephrased_question
                    }

                if not extracted_potential_models and not self.env.context.get('already_retried'):
                    return self.with_context(already_retried=True).compute_answer_action()

                generated = self.generate_model_fields_and_domain_query(
                    record.question,
                    rephrased_question=extracted_rephrased_question,
                    potential_models=extracted_potential_models,
                    important_words=extracted_tokens
                )

                actual_fields = generated.get('actual_fields') or generated.get('fields') or ['name']
                model = generated.get('model', 'res.partner')
                rephrased_question = generated.get("rephrased_question", extracted_rephrased_question)
                tokens = generated.get("tokens", extracted_tokens)

                general_answer = generated.get('general_answer', "")
                if general_answer:
                    record.answer = general_answer
                    return {
                        "answer": record.answer,
                        "models": generated.get('join_models', []) + [model],
                        "tokens": tokens,
                        "sql_query": generated.get("sql_query", ""),
                        "rephrased_question": rephrased_question
                    }

                if not generated.get('values') and not generated.get('sql_query'):
                    if self.env.context.get('already_retried'):
                        suggestions_html = self.get_gpt_suggestions(record.question)
                        record.answer = "❌ فشل في توليد استعلام أو عملية إنشاء صالحة." + suggestions_html
                        return {
                            "answer": record.answer,
                            "models": [model],
                            "tokens": tokens,
                            "sql_query": "",
                            "rephrased_question": rephrased_question
                        }
                    else:
                        return self.with_context(already_retried=True).compute_answer_action()

                if 'values' in generated:
                    values = generated.get('values', {})
                    orm_result = self.execute_orm_create_with_retries(
                        model=model,
                        values=values,
                        question=record.question,
                        question_lang=question_lang,
                        rephrased_question=rephrased_question,
                        tokens=tokens
                    )
                    record.answer = orm_result["result"]
                    return {
                        "answer": orm_result["result"],
                        "res": orm_result.get("res", False),
                        "models": generated.get('join_models', []) + [model],
                        "tokens": orm_result.get("tokens", []),
                        "sql_query": orm_result.get("sql_query", ""),
                        "rephrased_question": orm_result.get("rephrased_question", "")
                    }

                sql_query = generated.get('sql_query', "")
                sql_result = self.execute_sql_query_with_retries(
                    sql_query=sql_query,
                    actual_fields=actual_fields,
                    question=record.question,
                    question_lang=question_lang,
                    rephrased_question=rephrased_question,
                    tokens=tokens,
                    potential_models=extracted_potential_models
                )

                record.answer = sql_result["result"]
                return {
                    "res": sql_result.get("res", ""),
                    "answer": sql_result["result"],
                    "models": generated.get('join_models', []) + [model],
                    "tokens": sql_result.get("tokens", []),
                    "sql_query": sql_result.get("sql_query", ""),
                    "rephrased_question": sql_result.get("rephrased_question", "")
                }
        return {}

    def extract_important_words(self, text):
        client = self.get_openai_client()

        available_models = self.get_valid_model()
        try:
            question_analysis = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            """
                            📌 You are an AI assistant specialized in Odoo ERP.

                            🔍 STEP 1: Detect the type of operation:
                            - If the user's question is asking for data, statistics, totals, counts, or reports, then the operation_type is "SELECT".
                            - If the user's question is asking to create, add, insert, register, or log a new record, then the operation_type is "CREATE".

                            مع ضرورة الحفاظ التام على جميع الأسماء (مثل اسم العميل أو المورد أو المنتج) كما هي بدون أي تغيير أو تعديل أو ترجمة.
                            ✅ لا تلمّح ولا تستبدل أي قيمة تُستخدم للبحث مثل (اسم عميل - منتج - مورد).
                            ✅ الهدف أن يتم استخدام هذه القيم مباشرة في الاستعلام SQL أو ORM لضمان دقة النتائج.
                            مهمتك: إعادة صياغة السؤال التالي بلغة عربية فصحى رسمية أو تقنية دقيقة جدًا،
                            مع ضرورة الحفاظ التام على جميع الأسماء (مثل اسم العميل أو المورد أو المنتج) كما هي بدون أي تغيير أو تعديل أو ترجمة.
                            ✅ لا تلمّح ولا تستبدل أي قيمة تُستخدم للبحث مثل (اسم عميل - منتج - مورد).
                            ✅ الهدف أن يتم استخدام هذه القيم مباشرة في الاستعلام SQL أو ORM لضمان دقة النتائج.

                            ----------------------------------

                            ✅ استخدم دائمًا أحد القوالب التالية لإعادة صياغة السؤال:
                            - "ما هو عدد ... في حالة ..."
                             - "ما هو اسماء ... في حالة ..."

                            - "أرغب في معرفة تفاصيل ... المرتبطة بـ ..."
                            - "كم عدد ... التي تحتوي على ..."

                            ----------------------------------------------

                            Your task is to analyze the user's question carefully and return all Odoo models that are directly or indirectly required to answer the question.
                            Do NOT miss any related models, even if they are used in relations or joins.
                            Always return a JSON object with:
                            - 'question_type': either 'odoo_data' or 'general'.
                            - 'potential_models': a complete list of all relevant Odoo model technical names needed to answer the question.
                            - 'rephrased_question': The question rephrased clearly and technically.
                            - 'response': Only if question_type = 'general', include a friendly natural language answer to explain it.
                            Example:
                            {"question_type": "odoo_data", "potential_models": ["model1", "model2"], "rephrased_question": "...", "response": ""}
                            """
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: '{text}'\n"
                            "Your task is to rephrase the user's question into clear, formal, and technical Modern Standard Arabic.\n"
                            "✅ You must keep all names (such as partner names, product names, or vendor names) exactly as they appear — do NOT translate or modify them.\n"
                            "✅ Do NOT hint at or replace any value used for lookup (e.g., customer name, product name, supplier name).\n"
                            "✅ These values must be preserved as-is to ensure precise use in SQL or ORM operations.\n"
                            "\n"
                            "Your goal is to rewrite the question in a clear and unambiguous way that is suitable for direct interaction with Odoo ERP's database.\n"
                            "✅ Avoid vague, slang, or informal wording.\n"
                            "✅ Use precise financial, technical, or accounting terminology aligned with the Odoo ERP system.\n"
                            "✅ Do NOT add any explanations, notes, or comments — return only the rephrased question.\n"
                            "✅ The final rephrased question must be ready for SQL or ORM processing without requiring further clarification.\n"
                            "\n"
                            f"Available Odoo models: {available_models}\n"
                            "Please return:\n"
                            "- 'question_type': either 'general' (for explanations) or 'odoo_data' (for data retrieval or creation).\n"
                            "- 'potential_models': list of relevant Odoo models (from the provided list above) that are directly or indirectly needed to answer the question.\n"
                            "- 'rephrased_question': the rephrased question in precise Arabic.\n"
                            "- 'response': If question_type is 'general', return the friendly natural answer here. If it's 'odoo_data', leave response empty."
                        )
                    }
                ],
                temperature=0.0
            )
            response_content = question_analysis.choices[0].message.content.strip()
            raw_response = self.clean_code_response(response_content)
            analysis_result = self.clean_json_comments(raw_response)

            question_type = analysis_result.get("question_type", "general")
            potential_models = analysis_result.get("potential_models", [])
            rephrased_question = analysis_result.get("rephrased_question", text)
            general_response = analysis_result.get("response", "" if question_type == "odoo_data" else "No response.")

        except Exception as e:
            question_type = "general"
            potential_models = []
            rephrased_question = text
            general_response = ""

        tokens = []
        filtered_tokens = []
        extracted_data = {
            "tokens": tokens,
            "filtered_tokens": filtered_tokens,
            "question_type": question_type,
            "potential_models": potential_models,
            "rephrased_question": rephrased_question,
            "response": general_response
        }
        return extracted_data

    def execute_sql_query_with_retries(self, sql_query, actual_fields,
                                       question,
                                       question_lang,
                                       rephrased_question=None,
                                       tokens=None,
                                       potential_models=None,
                                       max_retries=1):

        attempt = 0
        last_error = None
        final_result = ""
        learning_trigger = False
        results = ""

        if not rephrased_question or not tokens or not potential_models:
            important_data = self.extract_important_words(question)
            potential_models = important_data["potential_models"]
            tokens = important_data["filtered_tokens"]
            rephrased_question = important_data["rephrased_question"]

        available_models_with_fields = self.get_available_models_with_fields(potential_models)
        executed_query = sql_query

        while attempt < max_retries:
            attempt += 1
            print(f"\nAttempt {attempt} to execute query...")
            try:
                if executed_query.strip().upper().startswith("SELECT"):
                    self.env.cr.execute(executed_query)
                    print(executed_query)
                    results = self.env.cr.fetchall()
                    print(results)

                    if (not results or
                            results == [(None,)] or
                            all(all(cell in (None, '', False) for cell in row) for row in results)):
                        suggestions_html = self.get_gpt_suggestions(rephrased_question)
                        final_result = (
                                           "No data found matching your query." if question_lang == "en"
                                           else "لم تُسفر نتائج البحث عن أي بيانات ذات صلة"
                                       ) + suggestions_html

                    else:
                        num_columns = len(results[0])
                        safe_fields = actual_fields[:num_columns]

                        non_empty_field_indexes = [
                            i for i, field in enumerate(safe_fields)
                            if any(row[i] not in (None, '', False) for row in results)
                        ]
                        filtered_fields = [safe_fields[i] for i in non_empty_field_indexes]

                        table_html = """
                        <table style="
                            border-collapse: collapse;
                            width: 100%;
                            text-align: center;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                        ">
                            <thead>
                                <tr style='background-color: #4CAF50; color: white;'>
                        """
                        for field in filtered_fields:
                            table_html += f"<th style='padding: 8px; border: 1px solid #ddd;'>{field}</th>"
                        table_html += "</tr></thead><tbody>"

                        for row in results:
                            table_html += "<tr>"
                            for i in non_empty_field_indexes:
                                table_html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{row[i]}</td>"
                            table_html += "</tr>"
                        table_html += "</tbody></table>"

                        final_result = table_html
                    break

                else:
                    self.env.cr.execute(executed_query)
                    print(executed_query)
                    self.env.cr.commit()
                    final_result = "✅ Operation completed successfully."
                    break

            except Exception as e:
                print(f"❌ Error executing SQL query on attempt {attempt}: {e}")
                last_error = str(e)
                self.env.cr.rollback()
                time.sleep(1)
                learning_trigger = True

                generated = self.generate_model_fields_and_domain_query(
                    question,
                    previous_query=executed_query,
                    error_message=last_error,
                    rephrased_question=rephrased_question,
                    potential_models=potential_models,
                    important_words=tokens,
                    available_models_with_fields=available_models_with_fields
                )
                new_sql_query = generated.get('sql_query', "")
                actual_fields = generated.get('actual_fields', [])
                if new_sql_query:
                    executed_query = new_sql_query
                    continue
                else:
                    print("Failed to regenerate SQL query.")
                    break

        if (not results or
                results == [(None,)] or
                all(all(cell in (None, '', False) for cell in row) for row in results)):
            suggestions_html = self.get_gpt_suggestions(rephrased_question)
            final_result = (
                               "No data found matching your query." if question_lang == "en"
                               else "لم تُسفر نتائج البحث عن أي بيانات ذات صلة"
                           ) + suggestions_html

        if learning_trigger and last_error:
            try:
                learning_result = self.generate_learning_instruction(
                    error_message=last_error,
                    previous_query=executed_query,
                    rephrased_question=rephrased_question,
                    available_models_with_fields={}
                )
                new_instruction = learning_result.get("new_instruction", "")
                corrected_sql = learning_result.get("correct_sql_query", "")

                if corrected_sql:
                    print("✅ Found corrected SQL from learning. Executing now...")
                    self.env.cr.execute(corrected_sql)
                    print(executed_query)

                    results = self.env.cr.fetchall()
                    print(results)

                    if (not results or
                            results == [(None,)] or
                            all(all(cell in (None, '', False) for cell in row) for row in results)):
                        suggestions_html = self.get_gpt_suggestions(rephrased_question)
                        final_result = (
                                           "No data found matching your query." if question_lang == "en"
                                           else "لم تُسفر نتائج البحث عن أي بيانات ذات صلة"
                                       ) + suggestions_html

                    else:
                        num_columns = len(results[0])
                        safe_fields = actual_fields[:num_columns]

                        non_empty_field_indexes = [
                            i for i, field in enumerate(safe_fields)
                            if any(row[i] not in (None, '', False) for row in results)
                        ]
                        filtered_fields = [safe_fields[i] for i in non_empty_field_indexes]

                        table_html = """
                        <table style="
                            border-collapse: collapse;
                            width: 100%;
                            text-align: center;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                        ">
                            <thead>
                                <tr style='background-color: #4CAF50; color: white;'>
                        """
                        for field in filtered_fields:
                            table_html += f"<th style='padding: 8px; border: 1px solid #ddd;'>{field}</th>"
                        table_html += "</tr></thead><tbody>"

                        for row in results:
                            table_html += "<tr>"
                            for i in non_empty_field_indexes:
                                table_html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{row[i]}</td>"
                            table_html += "</tr>"
                        table_html += "</tbody></table>"

                        return {
                            "res": results,
                            "result": table_html,
                            "sql_query": corrected_sql,
                            "tokens": tokens,
                            "rephrased_question": rephrased_question
                        }

                if new_instruction:
                    print(f"✅ Self-Learning Instruction: {new_instruction}")
                    self.append_instruction_to_system_prompt(f'"{new_instruction}"')

            except Exception as learn_ex:
                print(f"❌ Error during self-learning: {learn_ex}")
                self.env.cr.rollback()

        return {
            "res": results,
            "result": final_result,
            "sql_query": executed_query,
            "tokens": tokens,
            "rephrased_question": rephrased_question
        }

    def generate_model_fields_and_domain_query(self, question, values=None, previous_query=None, error_message=None,
                                               rephrased_question=None, potential_models=None, important_words=None,
                                               available_models_with_fields=None):
        client = self.get_openai_client()
        date_values = self.get_current_date_values()
        if not important_words or not potential_models:
            important_words_data = self.extract_important_words(question)
            important_words = important_words_data["filtered_tokens"]
            potential_models = important_words_data["potential_models"]
            question_type = important_words_data.get("question_type", "general")
            rephrased_question = important_words_data["rephrased_question"]
        else:
            print(" Reusing existing extracted tokens and models.")
        if not available_models_with_fields:
            available_models_with_fields = self.get_available_models_with_fields(potential_models)

        print(potential_models)
        system_prompt = self.load_system_prompt()

        try:
            result = {}
            if error_message:

                learning_result = self.generate_learning_instruction(
                    error_message=error_message,
                    previous_query=previous_query,
                    rephrased_question=rephrased_question,
                    available_models_with_fields={}
                )
                new_instruction = learning_result.get("new_instruction", "")

                print("1_2")

                self.append_instruction_to_system_prompt(f'"{new_instruction}"')


            else:
                user_message = (
                    f"Determines database operation type.\n"
                    f"Question: '{rephrased_question}'. \n"
                    f"Important words: {important_words}\n"
                    f"Available models WITH FIELDS: {available_models_with_fields}\n"
                    f"{'Previous SQL Query: ' + previous_query if previous_query else ''}\n"
                    f"{'Error encountered: ' + error_message if error_message else ''}\n"
                    f"{'Previous VALUES JSON: ' + json.dumps(values, ensure_ascii=False) if values else ''}\n"
                    "\n"
                    "If the domain contains fields of datatype 'date' and the question asks about the current year, month, or day, extract these values dynamically:\n"
                    f"- If the question refers to 'this year', use {date_values['current_year']} as the value.\n"
                    f"- If the question refers to 'this month', use the range '{date_values['first_day_of_month']}' to '{date_values['last_day_of_month']}'.\n"
                    f"- If the question refers to 'today', use '{datetime.today().strftime('%Y-%m-%d')}'.\n"
                    "\n"
                    "Note: For joining tables to obtain product names, always join product_product via product_id and then product_template using product_product.product_tmpl_id. Use product_template.name to display the final product name.\n"
                    "\n"
                    "This ensures the output is user-friendly and understandable to non-technical users.\n"

                    "\n📌 NOTE: Use the following instructions based on the detected operation type (SELECT or CREATE).\n"

                    "\n----------------------------------------\n"
                    "🎯 SELECT QUERIES: When the question asks for data, stats, or totals:\n"
                    "- Use only existing fields from the model.\n"
                    "- For relational fields, use JOINs to fetch display names.\n"
                    "- Avoid using GET_MODEL_ID — it's only for ORM.\n"
                    "- Cast JSONB fields before comparison (e.g., name::text).\n"
                    "- Include actual_fields to match columns with results.\n"
                    """
                    ❌ DO NOT embed SQL SELECT queries inside JSON values like domain or values.
                    ✅ Instead, return a clean domain using known field values or IDs only.
                    ✅ Example of valid domain: [["payment_state", "in", ["not_paid", "in_payment"]]]
                    ..
                    """

                "\n----------------------------------------\n"
                "🧱 ORM CREATION (CREATE operation):\n"
                "- Do NOT return SQL.\n"
                "- Return clean JSON with 'model', 'fields', and 'values'.\n"
                "- Use GET_MODEL_ID to fetch related record IDs dynamically.\n"
                "- For required fields like account_id, stop and return a general_answer if it's missing.\n"
                "\n💡 Example: \n"
                "{'operation_type': 'CREATE', 'model': 'res.partner', 'fields': [...], 'values': {...}}"

                "\n----------------------------------------\n"
                "🧠 GENERAL RULES:\n"
                "- Always verify model and field names.\n"
                "- Use underscores for table names (e.g., sale_order not sale.order).\n"
                "- Don't assume 'state' exists — check model fields first.\n"
                "- Always use JOIN for any readable info from related models (like partner name).\n"
                )
                response_full = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt

                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    temperature=0.0
                )

                raw_response = response_full.choices[0].message.content.strip()
                print("1_1")
                raw_response = self.clean_code_response(raw_response)
                result = self.clean_json_comments(raw_response)
                actual_fields = result.get("actual_fields", result.get("fields", []))

                models = result.get('join_models', []) + [result.get('model')]
        except Exception as e:
            print(f"Error generating full query: {e}")
            result = {
                "model": "",
                "fields": "",
                "domain": [],
                "sql_query": "",
                "join_models": []
            }

        return result

    def recursive_resolve_get_model_id(self, data):
        """
        Recursively traverse the input data and replace any string containing
        GET_MODEL_ID('model', 'field', 'value') with the corresponding record ID from the database.
        Supports nested dicts, lists, and one2many lines in Odoo-style tuples.
        """
        import re

        if isinstance(data, dict):
            return {key: self.recursive_resolve_get_model_id(value) for key, value in data.items()}

        elif isinstance(data, list):
            resolved_list = []
            for item in data:
                # Handle special one2many format: (0, 0, dict)
                if isinstance(item, tuple) and len(item) == 3 and item[0] == 0 and item[1] == 0 and isinstance(item[2],
                                                                                                               dict):
                    resolved_dict = self.recursive_resolve_get_model_id(item[2])
                    resolved_list.append((0, 0, resolved_dict))
                else:
                    resolved_list.append(self.recursive_resolve_get_model_id(item))
            return resolved_list

        elif isinstance(data, str) and 'GET_MODEL_ID' in data:
            model_call = re.findall(
                r"GET_MODEL_ID\(\s*['\"](.*?)['\"]\s*,\s*['\"](.*?)['\"]\s*,\s*['\"](.*?)['\"]\s*\)", data)
            if model_call:
                model, field, value = model_call[0]
                record = self.env[model].search([(field, '=', value)], limit=1)
                if not record:
                    raise ValueError(f"❌ لم يتم العثور على {model} حيث {field} = '{value}'")
                print(f"✅ تم استبدال GET_MODEL_ID('{model}', '{field}', '{value}') بـ ID: {record.id}")
                return record.id

        return data

    def finalize_odoo_orm_format(self, model, values):
        model_fields = self.env['ir.model.fields'].search([('model', '=', model), ('ttype', '=', 'one2many')])
        one2many_fields = [field.name for field in model_fields]

        for field_name in one2many_fields:
            if field_name in values and isinstance(values[field_name], list):
                final_lines = []
                for line in values[field_name]:
                    if isinstance(line, dict):
                        final_lines.append((0, 0, line))
                values[field_name] = final_lines
        return values

    def execute_orm_create_with_retries(self, model, values, question, question_lang, general_answer=None,
                                        rephrased_question=None, tokens=None, max_retries=3):
        if general_answer:
            print("⛔ تم إيقاف الـ ORM create بسبب وجود general_answer توضيحي.")
            return {
                "res": False,
                "result": general_answer,
                "tokens": tokens or [],
                "rephrased_question": rephrased_question,
                "sql_query": ""  # ORM doesn’t use SQL here
            }

        attempt = 0
        last_error = None
        learning_trigger = False
        created_record = False
        result_message = ""

        while attempt < max_retries:
            attempt += 1
            print(f"\n🔁 Attempt {attempt} to create ORM record for model '{model}'...")
            try:
                values = self.recursive_resolve_get_model_id(values)

                values = self.finalize_odoo_orm_format(model, values)

                if 'active' in values and model == 'account.move':
                    del values['active']

                created_record = self.env[model].create(values)
                result_message = f"✅ تم إنشاء السجل بنجاح (ID: {created_record.id})."
                print("✅ ORM record created successfully:", created_record)
                break

            except Exception as e:
                last_error = str(e)
                print(f"ORM creation failed on attempt {attempt}: {last_error}")
                self.env.cr.rollback()
                time.sleep(1)
                learning_trigger = True

                self.generate_model_fields_and_domain_query(
                    question,
                    values=values,
                    error_message=last_error,
                    rephrased_question=rephrased_question,
                    potential_models=[model],
                    important_words=tokens
                )

        if not created_record:
            suggestions_html = self.get_gpt_suggestions("❌ خطأ أثناء إنشاء السجل")

            result_message = f"❌ خطأ أثناء إنشاء السجل: {last_error}"+ suggestions_html

            if learning_trigger and last_error:
                try:
                    learning_result = self.generate_learning_instruction(
                        error_message=last_error,
                        previous_query=json.dumps(values, ensure_ascii=False),
                        rephrased_question=rephrased_question,
                        available_models_with_fields={model: {
                            'fields': list(values.keys())
                        }},
                        values=values
                    )
                    new_instruction = learning_result.get("new_instruction", "")
                    if new_instruction:
                        print(f"📚 تعليمات تعلم جديدة: {new_instruction}")
                        self.append_instruction_to_system_prompt(f'"{new_instruction}"')
                except Exception as learn_ex:
                    print(f"❌ خطأ أثناء توليد تعليمات التعلم: {learn_ex}")
                    self.env.cr.rollback()

        return {
            "res": created_record,
            "result": result_message,
            "tokens": tokens,
            "rephrased_question": rephrased_question,
            "sql_query": ""
        }

    def get_available_models_with_fields(self, potential_models):
        """
        Returns a dictionary with available models and their fields information.
        For each model, the result contains:
          - 'fields': List of valid field names.
          - 'fields_info': A dict with each field's type and string label.
          - 'selection_fields': For selection type fields, a list of selection values.
        """
        import json

        models_with_fields = {}

        if not potential_models:
            print("⚠️ No potential models detected. Returning empty models_with_fields.")
            return models_with_fields

        print(f"✅ Filtering only potential models: {potential_models}")
        models_rec = self.env['ir.model'].search([('model', 'in', potential_models)])
        print(f"✅ Fetched Models from ir.model: {[rec.model for rec in models_rec]}")

        for rec in models_rec:
            valid_fields = self.get_valid_fields(rec.model)
            fields_info = {}
            selection_fields = {}

            for field_name in valid_fields:
                try:
                    # استخدم fields_get للحصول على معلومات الحقل (النموذج، النوع، التسميات والقيم في حالة selection)
                    field_info = self.env[rec.model].fields_get(allfields=[field_name]).get(field_name, {})

                    # حفظ نوع الحقل واسم العرض (string) في fields_info
                    fields_info[field_name] = {
                        'type': field_info.get('type'),
                        'string': field_info.get('string', '')
                    }

                    # في حال كان الحقل من نوع selection، يتم استخراج القيم الخاصة به
                    if field_info.get('type') == 'selection':
                        selection_values = [item[0] for item in field_info.get('selection', [])]
                        selection_fields[field_name] = selection_values

                except Exception as e:
                    print(f"⚠️ Failed fetching selection for {field_name} in {rec.model}: {e}")

            if valid_fields:
                models_with_fields[rec.model] = {
                    'fields': valid_fields,
                    'fields_info': fields_info,
                    'selection_fields': selection_fields
                }
                print(
                    f"✅ Model: {rec.model} | Fields: {valid_fields} | Field Types: {json.dumps(fields_info, ensure_ascii=False)} | Selection Fields: {json.dumps(selection_fields, ensure_ascii=False)}"
                )

        return models_with_fields

    def generate_learning_instruction(self, error_message, previous_query, rephrased_question,
                                      available_models_with_fields, values=None, max_retries=3):
        client = self.get_openai_client()

        for attempt in range(1, max_retries + 1):
            try:
                learning_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a PostgreSQL SQL expert specialized in Odoo ERP systems.\n"
                                "✅ Your mission is to analyze the PostgreSQL SQL error and locate the exact cause of the failure.\n"
                                "✅ You must generate a permanent learning instruction to avoid this specific error in the future.\n\n"
                                "📌 تعليمات إضافية باللغة العربية:\n"
                                "Never use raw SQL queries inside any value of the domain. Always convert the logic into a proper Odoo domain using only available fields. For example, use [['product_id.default_code', '=', 'test']] instead of ['id', 'in', ['SELECT ...']]."
                                "✅ مع ضرورة الحفاظ التام على جميع الأسماء (مثل اسم العميل أو المورد أو المنتج) كما هي بدون أي تغيير أو تعديل أو ترجمة.\n"
                                "✅ لا تلمّح ولا تستبدل أي قيمة تُستخدم للبحث مثل (اسم عميل - منتج - مورد).\n"
                                "✅ الهدف أن يتم استخدام هذه القيم مباشرة في الاستعلام SQL أو ORM لضمان دقة النتائج.\n"
                                "✅ أنت مساعد ذكي متخصص في Odoo SQL وORM. مهمتك الآن توليد تعليمات تصحيحية تُضاف للاستعلام الحالي بحيث لا يتكرر الخطأ الذي حدث سابقاً.\n"
                                "✅ يجب أن تُرجع قاعدة أو تعليمات تصحيحية تُحدد بدقة كيف يجب تعديل الاستعلام لتلافي الخطأ نفسه في المحاولة القادمة.\n"
                                "✅ على سبيل المثال، إذا كان الخطأ ناتجًا عن عدم استخدام JOIN بالشكل الصحيح أو عن عدم وضع قيم نصية بين علامات اقتباس، فأنت مطالب بتوضيح ذلك بدقة.\n"
                                "❌ لا تُضف شرحًا إضافيًا أو أمثلة، فقط اذكر التعليمات بشكل موجز ورسمي.\n\n"
                                "✅ Technical Rules:\n"
                                "- You MUST mention the exact field name (e.g., product_template.name).\n"
                                "- If the error is due to jsonb ILIKE issue, the rule MUST explicitly state: Avoid using ILIKE on JSONB. Use name::text or name->>'lang' instead.\n"
                                "- NEVER generate generic rules. The rule MUST fix the error permanently.\n"
                                "- Example Correct Rule: Avoid using ILIKE directly on JSONB fields. Use name::text ILIKE or name->>'lang' instead.\n"
                                "- Write the rule formally and clearly in one paragraph.\n"
                                "- Focus on handling relational fields using NAME instead of IDs.\n"
                                "- DO NOT provide explanations or examples. Only generate the rule.\n\n"
                                "✅ The response MUST be strictly valid JSON containing ONLY:\n"
                                "- 'new_instruction': القاعدة التعليمية.\n"
                                "- 'correct_sql_query': الاستعلام بعد التصحيح.\n\n"
                                "⚠️ WARNING: You MUST ALWAYS return valid JSON. If you don't know the answer, return this:\n"
                                '{"new_instruction": "No new instruction. GPT could not analyze.", "correct_sql_query": ""}\n\n'
                                "✅ عند إرجاع الاستعلام SQL داخل JSON أو النص:\n"
                                "- لا تستخدم أي backslash \\ داخل القيم أو داخل الاستعلام.\n"
                                "- لو الاستعلام طويل، استخدم block code محاط بـsql... .\n"
                                "- تجنب الرموز التي تحتاج escape داخل JSON أو النص.\n"
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"🛑 Available models WITH FIELDS (use this for correct model-field mapping): {available_models_with_fields}\n"
                                f"📝 User Question: {rephrased_question}\n"
                                f"{'Previous SQL Query: ' + previous_query if previous_query else ''}\n"
                                f"{'Error encountered: ' + error_message if error_message else ''}\n"
                                f"{'Previous VALUES JSON: ' + json.dumps(values, ensure_ascii=False) if values else ''}\n"
                            )
                        }
                    ],
                    temperature=0.0)

                learning_text = learning_response.choices[0].message.content.strip()

                raw_response = self.clean_code_response(learning_text)
                raw_response = self.clean_json_comments(raw_response)
                new_instruction = raw_response.get("new_instruction", "")
                corrected_sql = raw_response.get("correct_sql_query", "")
                error_message = raw_response.get("error_message", "")
                print("inside_1")
                if new_instruction:
                    self.append_instruction_to_system_prompt(new_instruction)
                    self.load_system_prompt()

                return {"new_instruction": new_instruction,
                        "correct_sql_query": corrected_sql,
                        "error_message": error_message
                        }
                print("1_3")

            except Exception as e:
                print(f"❌ Attempt {attempt} - Error during learning: {e}")
                time.sleep(1)

        print("❌ All attempts failed. Returning fallback learning result.")
        return {"new_instruction": "",
                "correct_sql_query": "",
                "error_message": ""
                }

    def append_instruction_to_system_prompt(self, new_instruction):
        if not new_instruction:
            print("ℹ️ No new instruction to add.")
            return

        if isinstance(new_instruction, dict):
            try:
                import json
                new_instruction = json.dumps(new_instruction, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"❌ Failed to convert instruction to JSON string: {e}")
                return

        try:
            module_path = os.path.dirname(os.path.abspath(__file__))
            prompt_file = os.path.join(module_path, 'system_prompt.txt')
            with open(prompt_file, 'r', encoding='utf-8') as file:
                existing_content = file.read()

            with open(prompt_file, 'w', encoding='utf-8') as file:
                file.write(f"{new_instruction}\n\n# 🛠️ AUTO-GENERATED LEARNING\n\n" + existing_content)

            print("✅ تم حفظ التعليمات الجديدة في system_prompt.txt في بداية الملف")
        except Exception as e:
            print(f"❌ فشل أثناء كتابة التعليمات: {e}")

    def format_results_for_display(self, results, selected_fields):
        try:
            if results:
                formatted = []
                for rec in results:
                    row = []
                    for index, field in enumerate(selected_fields):
                        value = rec[index] if index < len(rec) else "غير متوفر"
                        row.append(f"{field}: {value}")
                    formatted.append(" | ".join(row))
                return "\n".join(formatted)
            else:
                suggestions_html = self.get_gpt_suggestions("لم يتم العثور على سجلات.")
                return "لم يتم العثور على سجلات."+ suggestions_html
        except Exception as e:
            print(f"Error formatting results: {e}")
            suggestions_html = self.get_gpt_suggestions("حدث خطأ أثناء تنسيق النتائج")
            return "حدث خطأ أثناء تنسيق النتائج." + suggestions_html

    def detect_language(self, text):
        arabic_pattern = re.compile("[\u0600-\u06FF]")
        english_pattern = re.compile("[a-zA-Z]")
        if arabic_pattern.search(text):
            return "ar"
        elif english_pattern.search(text):
            return "en"
        else:
            return "ar"

    def display_sql_result(self, results, selected_fields):
        if not results:
            return "<p>لا توجد نتائج لعرضها.</p>"

        table_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        table_html += "<thead><tr>"
        for field in selected_fields:
            table_html += f"<th style='background-color:#f2f2f2;padding:8px;text-align:right'>{field}</th>"
        table_html += "</tr></thead>"

        table_html += "<tbody>"
        for row in results:
            table_html += "<tr>"
            for cell in row:
                table_html += f"<td style='padding:8px;text-align:right'>{cell}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"

        return table_html

    def _save_question_answer_to_google_sheets(self, question, models, tokens, sql_query="", rephrased_question=""):
        try:
            if not question or not models or not tokens:
                print("❌ البيانات ناقصة، مش هنسجل.")
                return

            models_clean = [m if isinstance(m, str) else m.get("model", "") for m in models]

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
                ', '.join(models_clean),
                ', '.join(tokens),
                question,
                rephrased_question,
                sql_query
            ]

            worksheet.append_row(new_row, value_input_option='USER_ENTERED')
            row_number = len(worksheet.get_all_values())

            self.sheet_row_number = row_number
            print(f"✅ Saved to sheet, row number: {row_number}")
            return row_number
        except Exception as e:
            print(f"❌ Error saving to Google Sheet: {e}")

    def clean_json_comments(self, raw_response):
        """
        Clean and parse GPT response and ensure it's valid JSON.
        Raise detailed error if not parsable.
        """
        try:
            cleaned = re.sub(r"```[\w]*", "", raw_response, flags=re.MULTILINE)
            cleaned = cleaned.replace("```", "").strip()

            cleaned = re.sub(r'//.*', '', cleaned)
            cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

            if isinstance(cleaned, str):
                parsed_response = json.loads(cleaned)
            else:
                parsed_response = cleaned

            return parsed_response
        except Exception as e:
            raise ValueError(f"❌ Failed to parse valid JSON.\nRaw response: {raw_response}\nError: {str(e)}")

    def clean_code_response(self, raw_response):
        cleaned = re.sub(r"```[\w]*", "", raw_response, flags=re.MULTILINE)
        cleaned = cleaned.replace("```", "").strip()
        return cleaned

    def clean_model_name(self, model_name):
        cleaned_model = re.sub(r"[^\w.]", "", model_name).strip()
        print("Cleaned model name:", cleaned_model)
        return cleaned_model

    def get_valid_model(self):
        model_record = self.env['ir.model'].search([])
        return model_record

    def get_valid_fields(self, model_name):
        fields_rec = self.env['ir.model.fields'].search([
            ('model', '=', model_name),
            ('store', '=', True),
            ('ttype', 'not in', ('one2many', 'many2many'))
        ])
        valid_fields = [field.name for field in fields_rec] if fields_rec else []
        return valid_fields

    def get_available_models(self):
        models_rec = self.env['ir.model'].search([])
        available_models = [rec.model for rec in models_rec]
        return available_models

    def get_manual_search_instructions(self, model, question):
        client = self.get_openai_client()

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant specialized in Odoo. "
                            "Provide a concise, step-by-step guide in table format to help the user manually locate the required information in the Odoo UI."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: '{question}'\nModel: '{model}'\n"
                            "No results were found from the query. Please provide a clear step-by-step manual guide (preferably in table format) "
                            "to help the user locate this information in the Odoo interface."
                        )
                    }
                ]
            )
            manual_instructions = response.choices[0].message.content.strip()
            print("Manual search instructions:", manual_instructions)
            return manual_instructions
        except Exception as e:
            print(f"Error generating manual search instructions: {e}")
            return (
                " لم يتم العثور على نتائج.\n\n"
                "يرجى اتباع الخطوات التالية يدويًا:\n"
                "1. انتقل إلى الموديل المناسب عبر قائمة التطبيقات.\n"
                "2. استخدم شريط البحث لإدخال المعايير المطلوبة.\n"
                "3. تأكد من تحديد الفلاتر الصحيحة لمطابقة البيانات المطلوبة.\n"
                "4. إذا استمرت المشكلة، راجع إعدادات البحث أو استشر المسؤول."
            )

    def validate_sql_query(self, sql_query, main_model, join_models):
        valid_main_fields = self.get_valid_fields(main_model)
        valid_join_fields = {}
        for jm in join_models:
            valid_join_fields[jm] = self.get_valid_fields(jm)

        manual_mapping = {
            "sale.order.line": {
                "sale_order_id": "order_id"
            }
        }

        for jm in join_models:
            if jm in manual_mapping:
                for wrong_field, correct_field in manual_mapping[jm].items():
                    if wrong_field in sql_query and correct_field in valid_join_fields.get(jm, []):
                        sql_query = sql_query.replace(wrong_field, correct_field)

        return sql_query

    def get_current_date_values(self):
        today = datetime.today()
        current_year = today.year
        current_month = today.month
        current_day = today.day
        first_day_of_month = today.replace(day=1).strftime('%Y-%m-%d')
        last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1]).strftime('%Y-%m-%d')

        return {
            "current_year": current_year,
            "current_month": current_month,
            "current_day": current_day,
            "first_day_of_month": first_day_of_month,
            "last_day_of_month": last_day_of_month
        }

    def get_openai_client(self):
        ICP = self.env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('my_chatgpt_module.openapi_api_key')
        return OpenAI(api_key=api_key)

    def load_system_prompt(self):
        module_path = os.path.dirname(os.path.abspath(__file__))
        prompt_file = os.path.join(module_path, 'system_prompt.txt')
        with open(prompt_file, 'r', encoding='utf-8') as file:
            return file.read()

    def get_gpt_suggestions(self, failed_question):
        import html
        import re
        from markupsafe import Markup

        client = self.get_openai_client()
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "أنت مساعد ذكي في Odoo ERP. عند فشل استعلام المستخدم، اقترح عليه 3 إلى 5 أسئلة مشابهة قد تساعده "
                            "في الحصول على نتائج مفيدة. لا تشرح، فقط أعطه أسئلة بديلة بصيغة جاهزة باللغة العربية الفصحى."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"السؤال الذي فشل: {failed_question}\nرجاءً اقترح أسئلة بديلة للمستخدم."
                    }
                ],
                temperature=0.3
            )

            raw_content = response.choices[0].message.content
            print("🔎 Raw GPT content:\n", raw_content)

            suggestions = []
            for line in raw_content.strip().split('\n'):
                clean = re.sub(r'^[•\-–\d\.]*', '', line).strip()
                if clean and re.search(r'[\u0600-\u06FF]', clean):
                    suggestions.append(clean)

            print("✅ Final Cleaned Suggestions:", suggestions)

            if not suggestions:
                return Markup("<p style='color:gray;'>❗ لم يتم توليد أي اقتراحات مفهومة.</p>")

            html_output = '''
                <p style="margin-top:10px; margin-bottom:5px;">🔍 هل تريد أن تبحث:</p>
                <div style="display: flex; flex-direction: column; gap: 6px;">
            '''
            for s in suggestions:
                if not s or not isinstance(s, str):
                    continue
                clean_text = s.strip()
                html_output = """
                    <p style="margin-top:20px;">🔍 هل تريد أن تبحث:</p>
                    <div style="margin-top:10px;">
                    """
                for s in suggestions:
                    if not s or not isinstance(s, str):
                        continue
                    clean_text = s.strip()
                    html_output += f'''
                        <div class="gpt-suggestion-btn"
     data-question="{clean_text}"
     style="
        display: block !important;
        background: linear-gradient(to right, #e9f0ff, #f7faff);
        padding: 12px 16px;
        border-radius: 10px;
        font-size: 15px;
        color: #1a1a1a;
        border: 1px solid #cddff6;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        cursor: pointer !important;
        text-align: right;
        transition: background 0.3s ease;
        width: 100%;
        box-sizing: border-box;
    "
    onmouseover="this.style.backgroundColor='#d8e6fb';"
    onmouseout="this.style.backgroundColor='';">
    {clean_text}
</div>

                    '''

                html_output += "</div>"

            return Markup(html_output)

        except Exception as e:
            print("❌ Failed to generate suggestions:", e)
            return Markup("<p style='color:gray;'>💡 حاول استخدام صيغة مختلفة للسؤال.</p>")
