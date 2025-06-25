# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import requests, json
_logger = logging.getLogger(__name__)
from datetime import datetime,timedelta,time
import pytz

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]
def _tz_get(self):
    return _tzs
class BioTime(models.Model):
    _name = 'biotime.config'

    name = fields.Char(string="Name")
    server_url = fields.Char(string="Server URL", default="http://102.222.252.74:8081")
    username = fields.Char(string="Username")
    password = fields.Char(string="Password")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id)
    tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        default=lambda self: self._context.get('tz') or self.env.user.tz or self.env.ref('base.user_admin').tz or 'UTC',
        help="This field is used in order to define in which timezone the resources will work.")

    pull_from_date = fields.Datetime('Pull From Date')
    pull_to_date = fields.Datetime('Pull To Date')

    def action_pull_specific_dates(self):
        for rec in self.env['biotime.config'].sudo().search([]):
            rec.action_get_today_attendance(from_date=rec.pull_from_date, to_date=rec.pull_to_date)

    def generate_access_token(self):
        for rec in self:
            url = "%s/jwt-api-token-auth/" % rec.server_url
            payload = json.dumps({
                "username": rec.username,
                "password": rec.password
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.json()

    def action_get_all_terminals(self):
        for rec in self:
            terminal_env = self.env['biotime.terminal'].sudo()
            url = "%s/iclock/api/terminals/" % rec.server_url

            payload = {}
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'JWT %s' % rec.generate_access_token().get('token')
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            # print(response.text)
            data = response.json()
            if data.get('data'):
                for terminal in data['data']:
                    check = terminal_env.search([
                        ('biotime_id', '=', rec.id),
                        ('terminal_sn', '=', terminal.get('sn')),
                    ])
                    if not check:
                        terminal_env.create({
                            'name': terminal.get('terminal_name') if terminal.get('terminal_name') else 'New Device',
                            'terminal_id': terminal.get('id'),
                            'terminal_sn': terminal.get('sn'),
                            'ip_address': terminal.get('ip_address'),
                            'alias': terminal.get('alias'),
                            'terminal_tz': terminal.get('terminal_tz'),
                            'biotime_id': rec.id
                        })

    def action_get_all_employees(self, page=1):
        for rec in self:
            employee_env = self.env['biotime.employee'].sudo()
            url = "%s/personnel/api/employees/?page=%s" % (rec.server_url, page)

            payload = {}
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'JWT %s' % rec.generate_access_token().get('token')
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            # print(response.text)
            data = response.json()
            if data.get('data'):
                for employee in data['data']:
                    check = employee_env.search([
                        ('biotime_id', '=', rec.id),
                        ('employee_id', '=', employee.get('id')),
                    ])
                    if not check:
                        employee_env.create({
                            'name': employee.get('first_name'),
                            'employee_id': employee.get('id'),
                            'emp_code': employee.get('emp_code'),
                            'biotime_id': rec.id
                        })
                    else:
                        check.emp_code = employee.get('emp_code')
                        check.employee_id = employee.get('id')
            if data.get('next'):
                self.action_get_all_employees(page=data.get('next').split('page=')[1])

    def cron_get_today_attendance(self):
        for rec in self.env['biotime.config'].sudo().search([]):
            rec.action_get_today_attendance()

    def convert_to_utc(self, date, timezone):
        # Define the format of your datetime string
        date_format = '%Y-%m-%d %H:%M:%S'

        # إذا كان المدخل كائن datetime، استخدمه مباشرة
        if isinstance(date, datetime):
            local_dt = date
        else:
            # Convert the datetime string to a datetime object
            local_dt = datetime.strptime(date, date_format)

        # Localize the datetime object to your local time zone
        local_tz = pytz.timezone(timezone)
        local_dt = local_tz.localize(local_dt)

        # Convert the localized datetime to UTC
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt.strftime(date_format)

    def action_get_today_attendance(self, from_date=False, to_date=False):
        fixed_check_out_time = time(11, 00)  # 9:59 مساءً

        for rec in self:
            for tz in self.env['biotime.terminal'].sudo().search([('biotime_id', '=', rec.id)]):
                if from_date and to_date:
                    transactions = tz.action_get_transactions(from_date=rec.pull_from_date,
                                                              to_date=rec.pull_to_date).get('data')
                else:
                    transactions = tz.action_get_transactions().get('data')
                if transactions:
                    records = sorted(transactions, key=lambda x: x['punch_time'])
                    punches_by_employee = {}

                    # تجميع السجلات حسب الموظف
                    for record in records:
                        emp_code = record.get('emp_code')
                        punch_time = record.get('punch_time')

                        # تحويل punch_time إلى كائن datetime
                        if isinstance(punch_time, str):
                            punch_time = datetime.strptime(punch_time, "%Y-%m-%d %H:%M:%S")

                        if emp_code not in punches_by_employee:
                            punches_by_employee[emp_code] = []

                        if punches_by_employee[emp_code]:
                            last_punch_time = punches_by_employee[emp_code][-1]
                            time_diff = (punch_time - last_punch_time).total_seconds()

                            # إذا كان الفرق بين ثانية إلى دقيقتين، تجاوز السجل الحالي
                            if 1 <= time_diff <= 200:
                                continue

                        punches_by_employee[emp_code].append(punch_time)

                    # معالجة السجلات لكل موظف
                    for emp_code, punches in punches_by_employee.items():
                        check_employee = self.env['biotime.employee'].sudo().search([
                            ('emp_code', '=', emp_code),
                            ('biotime_id', '=', rec.id)
                        ], limit=1)

                        if check_employee and check_employee.odoo_employee_id:
                            odoo_employee_id = check_employee.odoo_employee_id.id

                            day_punches = {}
                            for punch_time in punches:
                                punch_date = punch_time.date()
                                if punch_date not in day_punches:
                                    day_punches[punch_date] = []
                                day_punches[punch_date].append(punch_time)

                            # معالجة السجلات لكل تاريخ
                            for punch_date, daily_punches in day_punches.items():
                                daily_punches = sorted(daily_punches)
                                for i in range(0, len(daily_punches), 2):
                                    check_in_time = daily_punches[i]
                                    str_check_in_time = rec.convert_to_utc(check_in_time, rec.tz)

                                    str_check_out_time = None

                                    if i + 1 < len(daily_punches):
                                        check_out_time = daily_punches[i + 1]
                                        str_check_out_time = rec.convert_to_utc(check_out_time, rec.tz)
                                    else:
                                        # إذا كان السجل الأخير ولا يحتوي على check_out
                                        current_time = datetime.now().time()
                                        start_time = time(23, 00)  # مثال: 8:00 مساءً
                                        end_time = time(23, 59)  # مثال: 11:59 مساءً

                                        if start_time <= current_time <= end_time:
                                            check_in_date = check_in_time.date()
                                            fixed_time = datetime.combine(check_in_date, fixed_check_out_time)
                                            str_check_out_time = fixed_time.strftime('%Y-%m-%d %H:%M:%S')

                                    existing_attendance = self.env['hr.attendance'].sudo().search([
                                        ('employee_id', '=', odoo_employee_id),
                                        ('check_in', '=', str_check_in_time),
                                    ], limit=1)

                                    if str_check_out_time:
                                        str_check_out_time_only = datetime.strptime(str_check_out_time,
                                                                                    '%Y-%m-%d %H:%M:%S').strftime(
                                            '%H:%M')
                                    else:
                                        str_check_out_time_only = None  # Or handle this case appropriately
                                    if existing_attendance:
                                        existing_attendance.write({'check_out': str_check_out_time,
                                                                   'is_put_by_system': True if str_check_out_time_only == '11:00' else False
                                                                   })
                                    else:
                                        if str_check_out_time:  # Ensure it's not False before parsing
                                            str_check_out_time_only = datetime.strptime(str_check_out_time,
                                                                                        '%Y-%m-%d %H:%M:%S').strftime(
                                                '%H:%M')

                                    if existing_attendance:
                                        existing_attendance.write({
                                            'check_out': str_check_out_time,
                                            'is_put_by_system': True if str_check_out_time_only == '11:00' else False

                                        })
                                    else:
                                        self.env['hr.attendance'].sudo().create({
                                            'employee_id': odoo_employee_id,
                                            'check_in': str_check_in_time,
                                            'check_out': str_check_out_time,
                                            'is_put_by_system': True if str_check_out_time_only == '11:00' else False
                                        })

    def get_datetime_in_riyadh_tz(self, datetime_value):
        """Convert given datetime to Riyadh timezone"""
        if datetime_value:
            # Get Egypt timezone
            riyadh_tz = pytz.timezone('Asia/Riyadh')
            utc_tz = pytz.utc
            utc_datetime = datetime_value.replace(tzinfo=utc_tz)

            # Convert UTC datetime to Egypt timezone
            riyadh_datetime = utc_datetime.astimezone(riyadh_tz)
            return riyadh_datetime

        return datetime_value

    # datetime_field = fields.Datetime(string="Datetime")

    # @api.onchange('datetime_field')
    # def onchange_datetime_field(self):
    #     """Example usage: Convert field to Saudi Arebia timezone"""
    #     if self.datetime_field:
    #         self.datetime_field = self.get_datetime_in_riyadh_tz(self.datetime_field)
