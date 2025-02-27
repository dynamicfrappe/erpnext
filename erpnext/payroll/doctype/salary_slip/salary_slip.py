# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
import datetime, math

from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words, formatdate
from frappe.model.naming import make_autoname

from frappe import msgprint, _
from erpnext.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils.background_jobs import enqueue
from erpnext.payroll.doctype.additional_salary.additional_salary import get_additional_salary_component
from erpnext.payroll.doctype.payroll_period.payroll_period import get_period_factor, get_payroll_period
from erpnext.payroll.doctype.employee_benefit_application.employee_benefit_application import get_benefit_component_amount
from erpnext.payroll.doctype.employee_benefit_claim.employee_benefit_claim import get_benefit_claim_amount, get_last_payroll_period_benefits
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import calculate_amounts, create_repayment_entry

class SalarySlip(TransactionBase):
	def __init__(self, *args, **kwargs):
		super(SalarySlip, self).__init__(*args, **kwargs)
		self.series = 'Sal Slip/{0}/.#####'.format(self.employee)
		self.whitelisted_globals = {
			"int": int,
			"float": float,
			"long": int,
			"round": round,
			"date": datetime.date,
			"getdate": getdate
		}

	def autoname(self):
		self.name = make_autoname(self.series)

	def update_salary_slip_in_additional_salary(self):
		salary_slip = self.name if self.docstatus == 1 else None
		names = []
		names.append('')
		for i in self.get("earnings") + self.get("deductions"):
			if i.additional_salary:
				ad_sal = frappe.get_doc("Additional Salary", i.additional_salary)
				if not ad_sal.is_recurring:
					if ad_sal and ad_sal.salary_slip and ad_sal.salary_slip != self.name:
						frappe.throw(_(
							"Please Recalculate Salary Slip {} <br> Additional Salary {} is duplicated in more than one Salary Slip".format(
								self.name, i.additional_salary)))

					names.append(i.additional_salary)
					names = tuple(names)
					# frappe.msgprint(sql)
					frappe.db.sql("""
						update `tabAdditional Salary` set salary_slip=%s
						where employee=%s and docstatus=1 and name in %s
					""", (salary_slip, self.employee, names))
				else:
					if salary_slip:
						# frappe.db.sql(
						#     """insert into  `tabAdditional Salary Salary Slips`  (salary_slip,parent,parenttype ,parentfield) values ('{}','{}','Additional Salary' , 'Salary Slips')""".format(self.name, ad_sal.name))

						ad_sal.append('salary_slips', {
							'salary_slip': salary_slip
						})
						ad_sal.save()
					else:
						frappe.db.sql(
							"""delete from `tabAdditional Salary Salary Slips` where parent = '{}' and salary_slip = '{}' """.format(
								ad_sal.name, self.name))

	def validate(self):
		self.status = self.get_status()
		self.validate_dates()
		self.check_existing()
		if not self.salary_slip_based_on_timesheet:
			self.get_date_details()

		if not (len(self.get("earnings")) or len(self.get("deductions"))):
			# get details from salary structure
			self.get_emp_and_working_day_details()
		else:
			self.get_working_days_details(lwp = self.leave_without_pay)

		self.calculate_net_pay()

		if frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet"):
			max_working_hours = frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet")
			if self.salary_slip_based_on_timesheet and (self.total_working_hours > int(max_working_hours)):
				frappe.msgprint(_("Total working hours should not be greater than max working hours {0}").
								format(max_working_hours), alert=True)

	def set_net_total_in_words(self):
		doc_currency = self.currency
		company_currency = erpnext.get_company_currency(self.company)
		total = self.net_pay if self.is_rounding_total_disabled() else self.rounded_total
		base_total = self.base_net_pay if self.is_rounding_total_disabled() else self.base_rounded_total
		self.total_in_words = money_in_words(total, doc_currency)
		self.base_total_in_words = money_in_words(base_total, company_currency)

	def on_submit(self):
		if self.net_pay < 0:
			frappe.throw(_("Net Pay cannot be less than 0"))
		else:
			self.set_status()
			self.update_status(self.name)
			self.make_loan_repayment_entry()
			self.update_salary_slip_in_additional_salary()

			if (frappe.db.get_single_value("Payroll Settings", "email_salary_slip_to_employee")) and not frappe.flags.via_payroll_entry:
				self.email_salary_slip()

	def on_cancel(self):
		self.set_status()
		self.update_status()
		self.cancel_loan_repayment_entry()
		self.update_salary_slip_in_additional_salary()

	def on_trash(self):
		from frappe.model.naming import revert_series_if_last
		revert_series_if_last(self.series, self.name)

	def get_status(self):
		if self.docstatus == 0:
			status = "Draft"
		elif self.docstatus == 1:
			status = "Submitted"
		elif self.docstatus == 2:
			status = "Cancelled"
		return status

	def validate_dates(self):
		if date_diff(self.end_date, self.start_date) < 0:
			frappe.throw(_("To date cannot be before From date"))

	def is_rounding_total_disabled(self):
		return cint(frappe.db.get_single_value("Payroll Settings", "disable_rounded_total"))

	def check_existing(self):
		if not self.salary_slip_based_on_timesheet:
			ret_exist = frappe.db.sql("""select name from `tabSalary Slip`
						where start_date = %s and end_date = %s and docstatus != 2
						and employee = %s and name != %s""",
						(self.start_date, self.end_date, self.employee, self.name))
			if ret_exist:
				self.employee = ''
				frappe.throw(_("Salary Slip of employee {0} already created for this period").format(self.employee))
		else:
			for data in self.timesheets:
				if frappe.db.get_value('Timesheet', data.time_sheet, 'status') == 'Payrolled':
					frappe.throw(_("Salary Slip of employee {0} already created for time sheet {1}").format(self.employee, data.time_sheet))

	def get_date_details(self):
		if not self.end_date:
			date_details = get_start_end_dates(self.payroll_frequency, self.start_date or self.posting_date)
			self.start_date = date_details.start_date
			self.end_date = date_details.end_date

	def get_emp_and_working_day_details(self):
		'''First time, load all the components from salary structure'''
		# frappe.msgprint(_("Salary Slip get_emp_and_working_day_details"))
		if self.employee:
			self.set("earnings", [])
			self.set("deductions", [])

			if not self.salary_slip_based_on_timesheet:
				self.get_date_details()
			self.validate_dates()
			joining_date, relieving_date = frappe.get_cached_value("Employee", self.employee,
				["date_of_joining", "relieving_date"])

			#getin leave details
			self.get_working_days_details(joining_date, relieving_date)
			struct = self.check_sal_struct(joining_date, relieving_date)

			if struct:

				self._salary_structure_doc = frappe.get_doc('Salary Structure', struct)
				self.salary_slip_based_on_timesheet = self._salary_structure_doc.salary_slip_based_on_timesheet or 0
				self.set_time_sheet()
				self.pull_sal_struct()
				# self.calculate_Tax()
				payroll_based_on, consider_unmarked_attendance_as = frappe.db.get_value("Payroll Settings", None, ["payroll_based_on","consider_unmarked_attendance_as"])
				return [payroll_based_on, consider_unmarked_attendance_as]

	def set_time_sheet(self):
		if self.salary_slip_based_on_timesheet:
			self.set("timesheets", [])
			timesheets = frappe.db.sql(""" select * from `tabTimesheet` where employee = %(employee)s and start_date BETWEEN %(start_date)s AND %(end_date)s and (status = 'Submitted' or
				status = 'Billed')""", {'employee': self.employee, 'start_date': self.start_date, 'end_date': self.end_date}, as_dict=1)

			for data in timesheets:
				self.append('timesheets', {
					'time_sheet': data.name,
					'working_hours': data.total_hours
				})

	def check_sal_struct(self, joining_date, relieving_date):
		cond = """and sa.employee=%(employee)s and (sa.from_date <= %(start_date)s or
				sa.from_date <= %(end_date)s or sa.from_date <= %(joining_date)s)"""
		if self.payroll_frequency:
			cond += """and ss.payroll_frequency = '%(payroll_frequency)s'""" % {"payroll_frequency": self.payroll_frequency}

		st_name = frappe.db.sql("""
			select sa.salary_structure
			from `tabSalary Structure Assignment` sa join `tabSalary Structure` ss
			where sa.salary_structure=ss.name
				and sa.docstatus = 1 and ss.docstatus = 1 and ss.is_active ='Yes' %s
			order by sa.from_date desc
			limit 1
		""" %cond, {'employee': self.employee, 'start_date': self.start_date,
			'end_date': self.end_date, 'joining_date': joining_date})

		if st_name:
			self.salary_structure = st_name[0][0]
			return self.salary_structure

		else:
			self.salary_structure = None
			frappe.msgprint(_("No active or default Salary Structure found for employee {0} for the given dates")
				.format(self.employee), title=_('Salary Structure Missing'))

	def pull_sal_struct(self):
		from erpnext.payroll.doctype.salary_structure.salary_structure import make_salary_slip

		if self.salary_slip_based_on_timesheet:
			self.salary_structure = self._salary_structure_doc.name
			self.hour_rate = self._salary_structure_doc.hour_rate
			self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
			self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
			wages_amount = self.hour_rate * self.total_working_hours

			self.add_earning_for_hourly_wages(self, self._salary_structure_doc.salary_component, wages_amount)

		make_salary_slip(self._salary_structure_doc.name, self)

	def get_working_days_details(self, joining_date=None, relieving_date=None, lwp=None, for_preview=0):
		payroll_based_on = frappe.db.get_value("Payroll Settings", None, "payroll_based_on")
		include_holidays_in_total_working_days = frappe.db.get_single_value("Payroll Settings", "include_holidays_in_total_working_days")

		working_days = date_diff(self.end_date, self.start_date) + 1
		if for_preview:
			self.total_working_days = working_days
			self.payment_days = working_days
			return

		holidays = self.get_holidays_for_employee(self.start_date, self.end_date)

		if not cint(include_holidays_in_total_working_days):
			working_days -= len(holidays)
			if working_days < 0:
				frappe.throw(_("There are more holidays than working days this month."))

		if not payroll_based_on:
			frappe.throw(_("Please set Payroll based on in Payroll settings"))

		if payroll_based_on == "Attendance":
			actual_lwp, absent = self.calculate_lwp_ppl_and_absent_days_based_on_attendance(holidays)
			self.absent_days = absent
		else:
			actual_lwp = self.calculate_lwp_or_ppl_based_on_leave_application(holidays, working_days)

		if not lwp:
			lwp = actual_lwp
		elif lwp != actual_lwp:
			frappe.msgprint(_("Leave Without Pay does not match with approved {} records")
				.format(payroll_based_on))

		self.leave_without_pay = lwp
		self.total_working_days = working_days

		payment_days = self.get_payment_days(joining_date,
			relieving_date, include_holidays_in_total_working_days)

		if flt(payment_days) > flt(lwp):
			self.payment_days = flt(payment_days) - flt(lwp)

			if payroll_based_on == "Attendance":
				self.payment_days -= flt(absent)

			unmarked_days = self.get_unmarked_days()
			consider_unmarked_attendance_as = frappe.db.get_value("Payroll Settings", None, "consider_unmarked_attendance_as") or "Present"

			if payroll_based_on == "Attendance" and consider_unmarked_attendance_as =="Absent":
				self.absent_days += unmarked_days #will be treated as absent
				self.payment_days -= unmarked_days
				if include_holidays_in_total_working_days:
					for holiday in holidays:
						if not frappe.db.exists("Attendance", {"employee": self.employee, "attendance_date": holiday, "docstatus": 1 }):
							self.payment_days += 1
		else:
			self.payment_days = 0

	def get_unmarked_days(self):
		marked_days = frappe.get_all("Attendance", filters = {
					"attendance_date": ["between", [self.start_date, self.end_date]],
					"employee": self.employee,
					"docstatus": 1
				}, fields = ["COUNT(*) as marked_days"])[0].marked_days

		return self.total_working_days - marked_days


	def get_payment_days(self, joining_date, relieving_date, include_holidays_in_total_working_days):
		if not joining_date:
			joining_date, relieving_date = frappe.get_cached_value("Employee", self.employee,
				["date_of_joining", "relieving_date"])

		start_date = getdate(self.start_date)
		if joining_date:
			if getdate(self.start_date) <= joining_date <= getdate(self.end_date):
				start_date = joining_date
			elif joining_date > getdate(self.end_date):
				return

		end_date = getdate(self.end_date)
		if relieving_date:
			if getdate(self.start_date) <= relieving_date <= getdate(self.end_date):
				end_date = relieving_date
			elif relieving_date < getdate(self.start_date):
				frappe.throw(_("Employee relieved on {0} must be set as 'Left'")
					.format(relieving_date))

		payment_days = date_diff(end_date, start_date) + 1

		if not cint(include_holidays_in_total_working_days):
			holidays = self.get_holidays_for_employee(start_date, end_date)
			payment_days -= len(holidays)

		return payment_days

	def get_holidays_for_employee(self, start_date, end_date):
		holiday_list = get_holiday_list_for_employee(self.employee)
		holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
			where
				parent=%(holiday_list)s
				and holiday_date >= %(start_date)s
				and holiday_date <= %(end_date)s''', {
					"holiday_list": holiday_list,
					"start_date": start_date,
					"end_date": end_date
				})

		holidays = [cstr(i) for i in holidays]

		return holidays

	def calculate_lwp_or_ppl_based_on_leave_application(self, holidays, working_days):
		lwp = 0
		holidays = "','".join(holidays)
		daily_wages_fraction_for_half_day = \
			flt(frappe.db.get_value("Payroll Settings", None, "daily_wages_fraction_for_half_day")) or 0.5

		for d in range(working_days):
			dt = add_days(cstr(getdate(self.start_date)), d)
			leave = frappe.db.sql("""
				SELECT t1.name,
					CASE WHEN (t1.half_day_date = %(dt)s or t1.to_date = t1.from_date)
					THEN t1.half_day else 0 END,
					t2.is_ppl,
					t2.fraction_of_daily_salary_per_leave
				FROM `tabLeave Application` t1, `tabLeave Type` t2
				WHERE t2.name = t1.leave_type
				AND (t2.is_lwp = 1 or t2.is_ppl = 1)
				AND t1.docstatus = 1
				AND t1.employee = %(employee)s
				AND ifnull(t1.salary_slip, '') = ''
				AND CASE
					WHEN t2.include_holiday != 1
						THEN %(dt)s not in ('{0}') and %(dt)s between from_date and to_date
					WHEN t2.include_holiday
						THEN %(dt)s between from_date and to_date
					END
				""".format(holidays), {"employee": self.employee, "dt": dt})

			if leave:
				equivalent_lwp_count = 0
				is_half_day_leave = cint(leave[0][1])
				is_partially_paid_leave = cint(leave[0][2])
				fraction_of_daily_salary_per_leave = flt(leave[0][3])

				equivalent_lwp_count =  (1 - daily_wages_fraction_for_half_day) if is_half_day_leave else 1

				if is_partially_paid_leave:
					equivalent_lwp_count *= fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1

				lwp += equivalent_lwp_count

		return lwp

	def calculate_lwp_ppl_and_absent_days_based_on_attendance(self, holidays):
		lwp = 0
		absent = 0

		daily_wages_fraction_for_half_day = \
			flt(frappe.db.get_value("Payroll Settings", None, "daily_wages_fraction_for_half_day")) or 0.5

		leave_types = frappe.get_all("Leave Type",
			or_filters=[["is_ppl", "=", 1], ["is_lwp", "=", 1]],
			fields =["name", "is_lwp", "is_ppl", "fraction_of_daily_salary_per_leave", "include_holiday"])

		leave_type_map = {}
		for leave_type in leave_types:
			leave_type_map[leave_type.name] = leave_type

		attendances = frappe.db.sql('''
			SELECT attendance_date, status, leave_type
			FROM `tabAttendance`
			WHERE
				status in ("Absent", "Half Day", "On leave")
				AND employee = %s
				AND docstatus = 1
				AND attendance_date between %s and %s
		''', values=(self.employee, self.start_date, self.end_date), as_dict=1)

		for d in attendances:
			if d.status in ('Half Day', 'On Leave') and d.leave_type and d.leave_type not in leave_type_map.keys():
				continue

			if formatdate(d.attendance_date, "yyyy-mm-dd") in holidays:
				if d.status == "Absent" or \
					(d.leave_type and d.leave_type in leave_type_map.keys() and not leave_type_map[d.leave_type]['include_holiday']):
						continue

			if d.leave_type:
				fraction_of_daily_salary_per_leave = leave_type_map[d.leave_type]["fraction_of_daily_salary_per_leave"]

			if d.status == "Half Day":
				equivalent_lwp =  (1 - daily_wages_fraction_for_half_day)

				if d.leave_type in leave_type_map.keys() and leave_type_map[d.leave_type]["is_ppl"]:
					equivalent_lwp *= fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
				lwp += equivalent_lwp
			elif d.status == "On Leave" and d.leave_type and d.leave_type in leave_type_map.keys():
				equivalent_lwp = 1
				if leave_type_map[d.leave_type]["is_ppl"]:
					equivalent_lwp *= fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
				lwp += equivalent_lwp
			elif d.status == "Absent":
				absent += 1
		return lwp, absent

	def add_earning_for_hourly_wages(self, doc, salary_component, amount):
		row_exists = False
		for row in doc.earnings:
			if row.salary_component == salary_component:
				row.amount = amount
				row_exists = True
				break

		if not row_exists:
			wages_row = {
				"salary_component": salary_component,
				"abbr": frappe.db.get_value("Salary Component", salary_component, "salary_component_abbr"),
				"amount": self.hour_rate * self.total_working_hours,
				"default_amount": 0.0,
				"additional_amount": 0.0
			}
			doc.append('earnings', wages_row)

	def calculate_net_pay(self):
		if self.salary_structure:
			self.calculate_component_amounts("earnings")
		self.gross_pay = self.get_component_totals("earnings")
		self.base_gross_pay = flt(flt(self.gross_pay) * flt(self.exchange_rate), self.precision('base_gross_pay'))

		if self.salary_structure:
			self.calculate_component_amounts("deductions")
		self.total_deduction = self.get_component_totals("deductions")
		self.base_total_deduction = flt(flt(self.total_deduction) * flt(self.exchange_rate), self.precision('base_total_deduction'))

		self.set_loan_repayment()

		self.net_pay = flt(self.gross_pay) - (flt(self.total_deduction) + flt(self.total_loan_repayment))
		self.rounded_total = rounded(self.net_pay)
		self.base_net_pay = flt(flt(self.net_pay) * flt(self.exchange_rate), self.precision('base_net_pay'))
		self.base_rounded_total = flt(rounded(self.base_net_pay), self.precision('base_net_pay'))
		if self.hour_rate:
			self.base_hour_rate = flt(flt(self.hour_rate) * flt(self.exchange_rate), self.precision('base_hour_rate'))
		self.set_net_total_in_words()

	def calculate_component_amounts(self, component_type):
		if not getattr(self, '_salary_structure_doc', None):
			self._salary_structure_doc = frappe.get_doc('Salary Structure', self.salary_structure)

		payroll_period = get_payroll_period(self.start_date, self.end_date, self.company)

		self.add_structure_components(component_type)
		self.add_additional_salary_components(component_type)
		if component_type == "earnings":
			self.add_employee_benefits(payroll_period)
		else:
			self.add_tax_components(payroll_period)

		self.set_component_amounts_based_on_payment_days(component_type)

	def add_structure_components(self, component_type):
		data = self.get_data_for_eval()
		for struct_row in self._salary_structure_doc.get(component_type):
			amount = self.eval_condition_and_formula(struct_row, data)
			if amount and struct_row.statistical_component == 0:
				self.update_component_row(struct_row, amount, component_type)

	def get_data_for_eval(self):
		'''Returns data for evaluating formula'''
		data = frappe._dict()

		data.update(frappe.get_doc("Salary Structure Assignment",
			{"employee": self.employee, "salary_structure": self.salary_structure}).as_dict())

		data.update(frappe.get_doc("Employee", self.employee).as_dict())
		data.update(self.as_dict())

		# set values for components
		salary_components = frappe.get_all("Salary Component", fields=["salary_component_abbr"])
		for sc in salary_components:
			data.setdefault(sc.salary_component_abbr, 0)

		for key in ('earnings', 'deductions'):
			for d in self.get(key):
				data[d.abbr] = d.amount

		return data

	def eval_condition_and_formula(self, d, data):
		try:
			condition = d.condition.strip().replace("\n", " ") if d.condition else None
			if condition:
				if not frappe.safe_eval(condition, self.whitelisted_globals, data):
					return None
			amount = d.amount
			if d.amount_based_on_formula:
				formula = d.formula.strip().replace("\n", " ") if d.formula else None
				if formula:
					amount = flt(frappe.safe_eval(formula, self.whitelisted_globals, data), d.precision("amount"))
			if amount:
				data[d.abbr] = amount

			return amount

		except NameError as err:
			frappe.throw(_("Name error: {0}").format(err))
		except SyntaxError as err:
			frappe.throw(_("Syntax error in formula or condition: {0}").format(err))
		except Exception as e:
			frappe.throw(_("Error in formula or condition: {0}").format(e))
			raise

	def add_employee_benefits(self, payroll_period):
		for struct_row in self._salary_structure_doc.get("earnings"):
			if struct_row.is_flexible_benefit == 1:
				if frappe.db.get_value("Salary Component", struct_row.salary_component, "pay_against_benefit_claim") != 1:
					benefit_component_amount = get_benefit_component_amount(self.employee, self.start_date, self.end_date,
						struct_row.salary_component, self._salary_structure_doc, self.payroll_frequency, payroll_period)
					if benefit_component_amount:
						self.update_component_row(struct_row, benefit_component_amount, "earnings")
				else:
					benefit_claim_amount = get_benefit_claim_amount(self.employee, self.start_date, self.end_date, struct_row.salary_component)
					if benefit_claim_amount:
						self.update_component_row(struct_row, benefit_claim_amount, "earnings")

		self.adjust_benefits_in_last_payroll_period(payroll_period)

	def adjust_benefits_in_last_payroll_period(self, payroll_period):
		if payroll_period:
			if (getdate(payroll_period.end_date) <= getdate(self.end_date)):
				last_benefits = get_last_payroll_period_benefits(self.employee, self.start_date, self.end_date,
					payroll_period, self._salary_structure_doc)
				if last_benefits:
					for last_benefit in last_benefits:
						last_benefit = frappe._dict(last_benefit)
						amount = last_benefit.amount
						self.update_component_row(frappe._dict(last_benefit.struct_row), amount, "earnings")

	def add_additional_salary_components(self, component_type):

		component_list = [i.salary_component for i in self.get("earnings") + self.get("deductions")]
		salary_components_details, additional_salary_details = get_additional_salary_component(self.employee,
			self.start_date, self.end_date, component_type , component_list)
		# frappe.msgprint(additional_salary_details)
		if salary_components_details and additional_salary_details:
			for additional_salary in additional_salary_details:
				additional_salary =frappe._dict(additional_salary)
				amount = additional_salary.amount
				overwrite = additional_salary.overwrite
				self.update_component_row(frappe._dict(salary_components_details[additional_salary.component]), amount,
					component_type, overwrite=overwrite, additional_salary=additional_salary.name)

	def calculate_Tax(self):
		total_taxable_amount = 0
		for e in self.get("earnings"):
			SC = frappe.get_doc("Salary Component", e.salary_component)
			if SC:
				if not SC.exempted_from_income_tax:
					total_taxable_amount += float(e.amount)

		for e in self.get("deductions"):
			SC = frappe.get_doc("Salary Component", e.salary_component)
			if SC:
				if not SC.exempted_from_income_tax:
					# frappe.msgprint(e.amount)
					total_taxable_amount -= float(e.amount)
		# total_taxable_amount -= self.social_insurance_amount
		self.tax_pool = total_taxable_amount or 0
		has_disability, is_consultant = frappe.db.get_value("Employee", self.employee,
															['has_disability', 'is_consultant'])
		total_tax = 0
		settings = frappe.get_single("Payroll Settings")
		Tax_Sc = settings.income_tax_salary_component or None
		personal_exemption_value = settings.personal_exemption_value or 0
		disability_exemption_value = settings.disability_exemption_value or 0

		if is_consultant:
			consultant_percent = settings.consultant_percent
			total_tax = total_taxable_amount * consultant_percent / 100
		else:
			total_tax_pool = frappe.db.sql("""
			select ifnull(sum(tax_pool),0) from `tabSalary Slip`
			where employee = '{employee}'  and month = '{month}' and name <> '{name}' """.format(
				month=self.month, employee=self.employee, name=self.name))[0][0] or 0
			total_taxable_amount += total_tax_pool

			if has_disability:
				personal_exemption_value += disability_exemption_value

			tax_layers = settings.tax_layers or None

			if Tax_Sc and tax_layers:

				if total_taxable_amount and total_taxable_amount > 0:
					total_taxable_amount_yearly = (total_taxable_amount * 12) - personal_exemption_value
					total_tax = 0
					perviuos_limit = 0
					total_taxable_amount_yearly = float(int(total_taxable_amount_yearly / 10) * 10)
					for i in tax_layers:
						if i.limit < total_taxable_amount_yearly:
							total_tax += (i.limit - perviuos_limit) * (i.tax_percent / 100)
							perviuos_limit = i.limit


						else:
							total_taxable_amount_yearly -= perviuos_limit
							total_tax += total_taxable_amount_yearly * (i.tax_percent / 100)
							break;
					total_tax = total_tax / 12
					self.tax_value = total_tax

		total_tax_value = frappe.db.sql("""
					select ifnull(sum(tax_value),0) from `tabSalary Slip`
					where employee = '{employee}'  and month = '{month}' and name <> '{name}' """.format(
			month=self.month, employee=self.employee, name=self.name))[0][0] or 0
		total_tax -= total_tax_value
		if total_tax < 0:
			total_tax = 0

		self.tax_value = total_tax or 0

		row = self.get_salary_slip_row(Tax_Sc)

		self.update_component_row(row, total_tax, "deductions", adding=1, adding_if_not_exist=1)

	def add_tax_components(self, payroll_period):
		# Calculate variable_based_on_taxable_salary after all components updated in salary slip
		tax_components, other_deduction_components = [], []
		for d in self._salary_structure_doc.get("deductions"):
			if d.variable_based_on_taxable_salary == 1 and not d.formula and not flt(d.amount):
				tax_components.append(d.salary_component)
			else:
				other_deduction_components.append(d.salary_component)

		if not tax_components:
			tax_components = [d.name for d in frappe.get_all("Salary Component", filters={"variable_based_on_taxable_salary": 1})
				if d.name not in other_deduction_components]

		for d in tax_components:
			tax_amount = self.calculate_variable_based_on_taxable_salary(d, payroll_period)
			tax_row = self.get_salary_slip_row(d)
			self.update_component_row(tax_row, tax_amount, "deductions")

	def update_component_row(self, struct_row, amount, key, overwrite=1, additional_salary = ''):
		component_row = None
		for d in self.get(key):
			if d.salary_component == struct_row.salary_component:
				component_row = d
		if not component_row or (struct_row.get("is_additional_component") and not overwrite):
			if amount:
				self.append(key, {
					'amount': amount,
					'default_amount': amount if not struct_row.get("is_additional_component") else 0,
					'depends_on_payment_days' : struct_row.depends_on_payment_days,
					'salary_component' : struct_row.salary_component,
					'abbr' : struct_row.abbr,
					'additional_salary': additional_salary,
					'do_not_include_in_total' : struct_row.do_not_include_in_total,
					'is_tax_applicable': struct_row.is_tax_applicable,
					'is_flexible_benefit': struct_row.is_flexible_benefit,
					'variable_based_on_taxable_salary': struct_row.variable_based_on_taxable_salary,
					'deduct_full_tax_on_selected_payroll_date': struct_row.deduct_full_tax_on_selected_payroll_date,
					'additional_amount': amount if struct_row.get("is_additional_component") else 0,
					'exempted_from_income_tax': struct_row.exempted_from_income_tax
				})
		else:
			if struct_row.get("is_additional_component"):
				if overwrite:
					component_row.additional_amount = amount - component_row.get("default_amount", 0)
					component_row.additional_salary = additional_salary
				else:
					component_row.additional_amount = amount

				if not overwrite and component_row.default_amount:
					amount += component_row.default_amount
			else:
				component_row.default_amount = amount

			component_row.amount = amount
			component_row.deduct_full_tax_on_selected_payroll_date = struct_row.deduct_full_tax_on_selected_payroll_date

	def calculate_variable_based_on_taxable_salary(self, tax_component, payroll_period):
		if not payroll_period:
			frappe.msgprint(_("Start and end dates not in a valid Payroll Period, cannot calculate {0}.")
				.format(tax_component))
			return

		# Deduct taxes forcefully for unsubmitted tax exemption proof and unclaimed benefits in the last period
		if payroll_period.end_date <= getdate(self.end_date):
			self.deduct_tax_for_unsubmitted_tax_exemption_proof = 1
			self.deduct_tax_for_unclaimed_employee_benefits = 1

		return self.calculate_variable_tax(payroll_period, tax_component)

	def calculate_variable_tax(self, payroll_period, tax_component):
		# get Tax slab from salary structure assignment for the employee and payroll period
		tax_slab = self.get_income_tax_slabs(payroll_period)

		# get remaining numbers of sub-period (period for which one salary is processed)
		remaining_sub_periods = get_period_factor(self.employee,
			self.start_date, self.end_date, self.payroll_frequency, payroll_period)[1]
		# get taxable_earnings, paid_taxes for previous period
		previous_taxable_earnings = self.get_taxable_earnings_for_prev_period(payroll_period.start_date,
			self.start_date, tax_slab.allow_tax_exemption)
		previous_total_paid_taxes = self.get_tax_paid_in_period(payroll_period.start_date, self.start_date, tax_component)

		# get taxable_earnings for current period (all days)
		current_taxable_earnings = self.get_taxable_earnings(tax_slab.allow_tax_exemption)
		future_structured_taxable_earnings = current_taxable_earnings.taxable_earnings * (math.ceil(remaining_sub_periods) - 1)

		# get taxable_earnings, addition_earnings for current actual payment days
		current_taxable_earnings_for_payment_days = self.get_taxable_earnings(tax_slab.allow_tax_exemption, based_on_payment_days=1)
		current_structured_taxable_earnings = current_taxable_earnings_for_payment_days.taxable_earnings
		current_additional_earnings = current_taxable_earnings_for_payment_days.additional_income
		current_additional_earnings_with_full_tax = current_taxable_earnings_for_payment_days.additional_income_with_full_tax

		# Get taxable unclaimed benefits
		unclaimed_taxable_benefits = 0
		if self.deduct_tax_for_unclaimed_employee_benefits:
			unclaimed_taxable_benefits = self.calculate_unclaimed_taxable_benefits(payroll_period)
			unclaimed_taxable_benefits += current_taxable_earnings_for_payment_days.flexi_benefits

		# Total exemption amount based on tax exemption declaration
		total_exemption_amount = self.get_total_exemption_amount(payroll_period, tax_slab)

		#Employee Other Incomes
		other_incomes = self.get_income_form_other_sources(payroll_period) or 0.0

		# Total taxable earnings including additional and other incomes
		total_taxable_earnings = previous_taxable_earnings + current_structured_taxable_earnings + future_structured_taxable_earnings \
			+ current_additional_earnings + other_incomes + unclaimed_taxable_benefits - total_exemption_amount

		# Total taxable earnings without additional earnings with full tax
		total_taxable_earnings_without_full_tax_addl_components = total_taxable_earnings - current_additional_earnings_with_full_tax

		# Structured tax amount
		total_structured_tax_amount = self.calculate_tax_by_tax_slab(
			total_taxable_earnings_without_full_tax_addl_components, tax_slab)
		current_structured_tax_amount = (total_structured_tax_amount - previous_total_paid_taxes) / remaining_sub_periods

		# Total taxable earnings with additional earnings with full tax
		full_tax_on_additional_earnings = 0.0
		if current_additional_earnings_with_full_tax:
			total_tax_amount = self.calculate_tax_by_tax_slab(total_taxable_earnings, tax_slab)
			full_tax_on_additional_earnings = total_tax_amount - total_structured_tax_amount

		current_tax_amount = current_structured_tax_amount + full_tax_on_additional_earnings
		if flt(current_tax_amount) < 0:
			current_tax_amount = 0

		return current_tax_amount

	def get_income_tax_slabs(self, payroll_period):
		income_tax_slab, ss_assignment_name = frappe.db.get_value("Salary Structure Assignment",
			{"employee": self.employee, "salary_structure": self.salary_structure, "docstatus": 1}, ["income_tax_slab", 'name'])

		if not income_tax_slab:
			frappe.throw(_("Income Tax Slab not set in Salary Structure Assignment: {0}").format(ss_assignment_name))

		income_tax_slab_doc = frappe.get_doc("Income Tax Slab", income_tax_slab)
		if income_tax_slab_doc.disabled:
			frappe.throw(_("Income Tax Slab: {0} is disabled").format(income_tax_slab))

		if getdate(income_tax_slab_doc.effective_from) > getdate(payroll_period.start_date):
			frappe.throw(_("Income Tax Slab must be effective on or before Payroll Period Start Date: {0}")
				.format(payroll_period.start_date))

		return income_tax_slab_doc


	def get_taxable_earnings_for_prev_period(self, start_date, end_date, allow_tax_exemption=False):
		taxable_earnings = frappe.db.sql("""
			select sum(sd.amount)
			from
				`tabSalary Detail` sd join `tabSalary Slip` ss on sd.parent=ss.name
			where
				sd.parentfield='earnings'
				and sd.is_tax_applicable=1
				and is_flexible_benefit=0
				and ss.docstatus=1
				and ss.employee=%(employee)s
				and ss.start_date between %(from_date)s and %(to_date)s
				and ss.end_date between %(from_date)s and %(to_date)s
			""", {
				"employee": self.employee,
				"from_date": start_date,
				"to_date": end_date
			})
		taxable_earnings = flt(taxable_earnings[0][0]) if taxable_earnings else 0

		exempted_amount = 0
		if allow_tax_exemption:
			exempted_amount = frappe.db.sql("""
				select sum(sd.amount)
				from
					`tabSalary Detail` sd join `tabSalary Slip` ss on sd.parent=ss.name
				where
					sd.parentfield='deductions'
					and sd.exempted_from_income_tax=1
					and is_flexible_benefit=0
					and ss.docstatus=1
					and ss.employee=%(employee)s
					and ss.start_date between %(from_date)s and %(to_date)s
					and ss.end_date between %(from_date)s and %(to_date)s
				""", {
					"employee": self.employee,
					"from_date": start_date,
					"to_date": end_date
				})
			exempted_amount = flt(exempted_amount[0][0]) if exempted_amount else 0

		return taxable_earnings - exempted_amount

	def get_tax_paid_in_period(self, start_date, end_date, tax_component):
		# find total_tax_paid, tax paid for benefit, additional_salary
		total_tax_paid = flt(frappe.db.sql("""
			select
				sum(sd.amount)
			from
				`tabSalary Detail` sd join `tabSalary Slip` ss on sd.parent=ss.name
			where
				sd.parentfield='deductions'
				and sd.salary_component=%(salary_component)s
				and sd.variable_based_on_taxable_salary=1
				and ss.docstatus=1
				and ss.employee=%(employee)s
				and ss.start_date between %(from_date)s and %(to_date)s
				and ss.end_date between %(from_date)s and %(to_date)s
		""", {
			"salary_component": tax_component,
			"employee": self.employee,
			"from_date": start_date,
			"to_date": end_date
		})[0][0])

		return total_tax_paid

	def get_taxable_earnings(self, allow_tax_exemption=False, based_on_payment_days=0):
		joining_date, relieving_date = frappe.get_cached_value("Employee", self.employee,
			["date_of_joining", "relieving_date"])

		if not relieving_date:
			relieving_date = getdate(self.end_date)

		if not joining_date:
			frappe.throw(_("Please set the Date Of Joining for employee {0}").format(frappe.bold(self.employee_name)))

		taxable_earnings = 0
		additional_income = 0
		additional_income_with_full_tax = 0
		flexi_benefits = 0

		for earning in self.earnings:
			if based_on_payment_days:
				amount, additional_amount = self.get_amount_based_on_payment_days(earning, joining_date, relieving_date)
			else:
				amount, additional_amount = earning.amount, earning.additional_amount

			if earning.is_tax_applicable:
				if additional_amount:
					taxable_earnings += (amount - additional_amount)
					additional_income += additional_amount
					if earning.deduct_full_tax_on_selected_payroll_date:
						additional_income_with_full_tax += additional_amount
					continue

				if earning.is_flexible_benefit:
					flexi_benefits += amount
				else:
					taxable_earnings += amount

		if allow_tax_exemption:
			for ded in self.deductions:
				if ded.exempted_from_income_tax:
					amount = ded.amount
					if based_on_payment_days:
						amount = self.get_amount_based_on_payment_days(ded, joining_date, relieving_date)[0]
					taxable_earnings -= flt(amount)

		return frappe._dict({
			"taxable_earnings": taxable_earnings,
			"additional_income": additional_income,
			"additional_income_with_full_tax": additional_income_with_full_tax,
			"flexi_benefits": flexi_benefits
		})

	def get_amount_based_on_payment_days(self, row, joining_date, relieving_date):
		amount, additional_amount = row.amount, row.additional_amount
		if (self.salary_structure and
			cint(row.depends_on_payment_days) and cint(self.total_working_days) and
			(not self.salary_slip_based_on_timesheet or
				getdate(self.start_date) < joining_date or
				getdate(self.end_date) > relieving_date
			)):
			additional_amount = flt((flt(row.additional_amount) * flt(self.payment_days)
				/ cint(self.total_working_days)), row.precision("additional_amount"))
			amount = flt((flt(row.default_amount) * flt(self.payment_days)
				/ cint(self.total_working_days)), row.precision("amount")) + additional_amount

		elif not self.payment_days and not self.salary_slip_based_on_timesheet and cint(row.depends_on_payment_days):
			amount, additional_amount = 0, 0
		elif not row.amount:
			amount = flt(row.default_amount) + flt(row.additional_amount)

		# apply rounding
		if frappe.get_cached_value("Salary Component", row.salary_component, "round_to_the_nearest_integer"):
			amount, additional_amount = rounded(amount), rounded(additional_amount)

		return amount, additional_amount

	def calculate_unclaimed_taxable_benefits(self, payroll_period):
		# get total sum of benefits paid
		total_benefits_paid = flt(frappe.db.sql("""
			select sum(sd.amount)
			from `tabSalary Detail` sd join `tabSalary Slip` ss on sd.parent=ss.name
			where
				sd.parentfield='earnings'
				and sd.is_tax_applicable=1
				and is_flexible_benefit=1
				and ss.docstatus=1
				and ss.employee=%(employee)s
				and ss.start_date between %(start_date)s and %(end_date)s
				and ss.end_date between %(start_date)s and %(end_date)s
		""", {
			"employee": self.employee,
			"start_date": payroll_period.start_date,
			"end_date": self.start_date
		})[0][0])

		# get total benefits claimed
		total_benefits_claimed = flt(frappe.db.sql("""
			select sum(claimed_amount)
			from `tabEmployee Benefit Claim`
			where
				docstatus=1
				and employee=%s
				and claim_date between %s and %s
		""", (self.employee, payroll_period.start_date, self.end_date))[0][0])

		return total_benefits_paid - total_benefits_claimed

	def get_total_exemption_amount(self, payroll_period, tax_slab):
		total_exemption_amount = 0
		if tax_slab.allow_tax_exemption:
			if self.deduct_tax_for_unsubmitted_tax_exemption_proof:
				exemption_proof = frappe.db.get_value("Employee Tax Exemption Proof Submission",
					{"employee": self.employee, "payroll_period": payroll_period.name, "docstatus": 1},
					["exemption_amount"])
				if exemption_proof:
					total_exemption_amount = exemption_proof
			else:
				declaration = frappe.db.get_value("Employee Tax Exemption Declaration",
					{"employee": self.employee, "payroll_period": payroll_period.name, "docstatus": 1},
					["total_exemption_amount"])
				if declaration:
					total_exemption_amount = declaration

			total_exemption_amount += flt(tax_slab.standard_tax_exemption_amount)

		return total_exemption_amount

	def get_income_form_other_sources(self, payroll_period):
		return frappe.get_all("Employee Other Income",
			filters={
				"employee": self.employee,
				"payroll_period": payroll_period.name,
				"company": self.company,
				"docstatus": 1
			},
			fields="SUM(amount) as total_amount"
		)[0].total_amount

	def calculate_tax_by_tax_slab(self, annual_taxable_earning, tax_slab):
		data = self.get_data_for_eval()
		data.update({"annual_taxable_earning": annual_taxable_earning})
		tax_amount = 0
		for slab in tax_slab.slabs:
			if slab.condition and not self.eval_tax_slab_condition(slab.condition, data):
				continue
			if not slab.to_amount and annual_taxable_earning >= slab.from_amount:
				tax_amount += (annual_taxable_earning - slab.from_amount + 1) * slab.percent_deduction *.01
				continue
			if annual_taxable_earning >= slab.from_amount and annual_taxable_earning < slab.to_amount:
				tax_amount += (annual_taxable_earning - slab.from_amount + 1) * slab.percent_deduction *.01
			elif annual_taxable_earning >= slab.from_amount and annual_taxable_earning >= slab.to_amount:
				tax_amount += (slab.to_amount - slab.from_amount + 1) * slab.percent_deduction * .01

		# other taxes and charges on income tax
		for d in tax_slab.other_taxes_and_charges:
			if flt(d.min_taxable_income) and flt(d.min_taxable_income) > annual_taxable_earning:
				continue

			if flt(d.max_taxable_income) and flt(d.max_taxable_income) < annual_taxable_earning:
				continue

			tax_amount += tax_amount * flt(d.percent) / 100

		return tax_amount

	def eval_tax_slab_condition(self, condition, data):
		try:
			condition = condition.strip()
			if condition:
				return frappe.safe_eval(condition, self.whitelisted_globals, data)
		except NameError as err:
			frappe.throw(_("Name error: {0}").format(err))
		except SyntaxError as err:
			frappe.throw(_("Syntax error in condition: {0}").format(err))
		except Exception as e:
			frappe.throw(_("Error in formula or condition: {0}").format(e))
			raise

	def get_salary_slip_row(self, salary_component):
		component = frappe.get_doc("Salary Component", salary_component)
		# Data for update_component_row
		struct_row = frappe._dict()
		struct_row['depends_on_payment_days'] = component.depends_on_payment_days
		struct_row['salary_component'] = component.name
		struct_row['abbr'] = component.salary_component_abbr
		struct_row['do_not_include_in_total'] = component.do_not_include_in_total
		struct_row['is_tax_applicable'] = component.is_tax_applicable
		struct_row['is_flexible_benefit'] = component.is_flexible_benefit
		struct_row['variable_based_on_taxable_salary'] = component.variable_based_on_taxable_salary
		return struct_row

	def get_component_totals(self, component_type):
		total = 0.0
		for d in self.get(component_type):
			if not d.do_not_include_in_total:
				d.amount = flt(d.amount, d.precision("amount"))
				total += d.amount
		return total

	def set_component_amounts_based_on_payment_days(self, component_type):
		joining_date, relieving_date = frappe.get_cached_value("Employee", self.employee,
			["date_of_joining", "relieving_date"])

		if not relieving_date:
			relieving_date = getdate(self.end_date)

		if not joining_date:
			frappe.throw(_("Please set the Date Of Joining for employee {0}").format(frappe.bold(self.employee_name)))

		for d in self.get(component_type):
			d.amount = self.get_amount_based_on_payment_days(d, joining_date, relieving_date)[0]

	def set_loan_repayment(self):
		self.total_loan_repayment = 0
		self.total_interest_amount = 0
		self.total_principal_amount = 0

		if not self.get('loans'):
			for loan in self.get_loan_details():
				frappe.throw("ACCC" , self.end_date)
				amounts = calculate_amounts(loan.name, self.posting_date, "Regular Payment")

				if amounts['interest_amount'] or amounts['payable_principal_amount']:

					self.append('loans', {
						'loan': loan.name,
						'total_payment': amounts['interest_amount'] + amounts['payable_principal_amount'],
						'interest_amount': amounts['interest_amount'],
						'principal_amount': amounts['payable_principal_amount'],
						'loan_account': loan.loan_account,
						'interest_income_account': loan.interest_income_account
					})

		for payment in self.get('loans'):
			frappe.throw("ACCC" , self.end_date)
			amounts = calculate_amounts(payment.loan, self.end_date, "Regular Payment")
			total_amount = amounts['interest_amount'] + amounts['payable_principal_amount']
			if payment.total_payment > total_amount:
				frappe.throw(_("""Row {0}: Paid amount {1} is greater than pending accrued amount {2} against loan {3}""")
					.format(payment.idx, frappe.bold(payment.total_payment),
						frappe.bold(total_amount), frappe.bold(payment.loan)))

			self.total_interest_amount += payment.interest_amount
			self.total_principal_amount += payment.principal_amount

			self.total_loan_repayment += payment.total_payment

	def get_loan_details(self):

		return frappe.get_all("Loan",
			fields=["name", "interest_income_account", "loan_account", "loan_type"],
			filters = {
				"applicant": self.employee,
				"docstatus": 1,
				"repay_from_salary": 1,
			})

	def make_loan_repayment_entry(self):
		for loan in self.loans:
			repayment_entry = create_repayment_entry(loan.loan, self.employee,
				self.company, self.posting_date, loan.loan_type, "Regular Payment", loan.interest_amount,
				loan.principal_amount, loan.total_payment)

			repayment_entry.save()
			repayment_entry.submit()

			loan.loan_repayment_entry = repayment_entry.name

	def cancel_loan_repayment_entry(self):
		for loan in self.loans:
			if loan.loan_repayment_entry:
				repayment_entry = frappe.get_doc("Loan Repayment", loan.loan_repayment_entry)
				repayment_entry.cancel()

	def email_salary_slip(self):
		receiver = frappe.db.get_value("Employee", self.employee, "prefered_email")
		payroll_settings = frappe.get_single("Payroll Settings")
		message = "Please see attachment"
		password = None
		if payroll_settings.encrypt_salary_slips_in_emails:
			password = generate_password_for_pdf(payroll_settings.password_policy, self.employee)
			message += """<br>Note: Your salary slip is password protected,
				the password to unlock the PDF is of the format {0}. """.format(payroll_settings.password_policy)

		if receiver:
			email_args = {
				"recipients": [receiver],
				"message": _(message),
				"subject": 'Salary Slip - from {0} to {1}'.format(self.start_date, self.end_date),
				"attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name, password=password)],
				"reference_doctype": self.doctype,
				"reference_name": self.name
				}
			if not frappe.flags.in_test:
				enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
			else:
				frappe.sendmail(**email_args)
		else:
			msgprint(_("{0}: Employee email not found, hence email not sent").format(self.employee_name))

	def update_status(self, salary_slip=None):
		for data in self.timesheets:
			if data.time_sheet:
				timesheet = frappe.get_doc('Timesheet', data.time_sheet)
				timesheet.salary_slip = salary_slip
				timesheet.flags.ignore_validate_update_after_submit = True
				timesheet.set_status()
				timesheet.save()

	def set_status(self, status=None):
		'''Get and update status'''
		if not status:
			status = self.get_status()
		self.db_set("status", status)


	def process_salary_structure(self, for_preview=0):
		'''Calculate salary after salary structure details have been updated'''
		if not self.salary_slip_based_on_timesheet:
			self.get_date_details()
		self.pull_emp_details()
		self.get_working_days_details(for_preview=for_preview)
		self.calculate_net_pay()

	def pull_emp_details(self):
		emp = frappe.db.get_value("Employee", self.employee, ["bank_name", "bank_ac_no", "salary_mode"], as_dict=1)
		if emp:
			self.mode_of_payment = emp.salary_mode
			self.bank_name = emp.bank_name
			self.bank_account_no = emp.bank_ac_no

	def process_salary_based_on_working_days(self):
		self.get_working_days_details(lwp=self.leave_without_pay)
		self.calculate_net_pay()

	def set_totals(self):
		self.gross_pay = 0
		if self.salary_slip_based_on_timesheet == 1:
			self.calculate_total_for_salary_slip_based_on_timesheet()
		else:
			self.total_deduction = 0
			if hasattr (self,"earnings"):
				for earning in self.earnings:
					self.gross_pay += flt(earning.amount)
			if hasattr(self, "deductions"):

				for deduction in self.deductions:
					self.total_deduction += flt(deduction.amount)
			self.net_pay = flt(self.gross_pay) - flt(self.total_deduction) - flt(self.total_loan_repayment)
		self.set_base_totals()

	def set_base_totals(self):
		self.base_gross_pay = flt(self.gross_pay) * flt(self.exchange_rate)
		self.base_total_deduction = flt(self.total_deduction) * flt(self.exchange_rate)
		self.rounded_total = rounded(self.net_pay)
		self.base_net_pay = flt(self.net_pay) * flt(self.exchange_rate)
		self.base_rounded_total = rounded(self.base_net_pay)
		self.set_net_total_in_words()

	#calculate total working hours, earnings based on hourly wages and totals
	def calculate_total_for_salary_slip_based_on_timesheet(self):
		if self.timesheets:
			for timesheet in self.timesheets:
				if timesheet.working_hours:
					self.total_working_hours += timesheet.working_hours

		wages_amount = self.total_working_hours * self.hour_rate
		self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
		# frappe.msgprint("self.salary_structure {} ".format(self.salary_structure))
		salary_component = frappe.db.get_value('Salary Structure', {'name': self.salary_structure}, 'salary_component')
		if self.earnings:
			for i, earning in enumerate(self.earnings):
				if earning.salary_component == salary_component:
					self.earnings[i].amount = wages_amount
				self.gross_pay += self.earnings[i].amount
		self.net_pay = flt(self.gross_pay) - flt(self.total_deduction)

def unlink_ref_doc_from_salary_slip(ref_no):
	linked_ss = frappe.db.sql_list("""select name from `tabSalary Slip`
	where journal_entry=%s and docstatus < 2""", (ref_no))
	if linked_ss:
		for ss in linked_ss:
			ss_doc = frappe.get_doc("Salary Slip", ss)
			frappe.db.set_value("Salary Slip", ss_doc.name, "journal_entry", "")

def generate_password_for_pdf(policy_template, employee):
	employee = frappe.get_doc("Employee", employee)
	return policy_template.format(**employee.as_dict())
try:
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import get_emp_and_working_day_details
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import calculate_Tax
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import get_Employee_advance
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import get_social_insurance
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import get_medical_insurance
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import add_structure_components
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import check_sal_struct
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import calculate_component_amounts
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import add_additional_salary_components
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import pull_sal_struct
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import pull_sal_struct
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import pull_sal_struct
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  get_data_for_eval
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  eval_condition_and_formula
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  update_component_row
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  on_submit
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  calculate_net_pay
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  set_totals
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  update_salary_slip_in_additional_salary
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  set_loan_repayment
	from dynamicerp.dynamic_payroll.doctype.salary_slip.salary_slip import  make_loan_repayment_entry

	SalarySlip.get_emp_and_working_day_details = get_emp_and_working_day_details
	SalarySlip.calculate_Tax = calculate_Tax
	SalarySlip.get_Employee_advance = get_Employee_advance
	SalarySlip.get_social_insurance = get_social_insurance
	SalarySlip.get_medical_insurance = get_medical_insurance
	SalarySlip.add_structure_components = add_structure_components
	SalarySlip.check_sal_struct = check_sal_struct
	SalarySlip.calculate_component_amounts = calculate_component_amounts
	SalarySlip.pull_sal_struct = pull_sal_struct
	SalarySlip.add_additional_salary_components = add_additional_salary_components
	SalarySlip.eval_condition_and_formula = eval_condition_and_formula
	SalarySlip.get_data_for_eval = get_data_for_eval
	SalarySlip.update_component_row = update_component_row
	SalarySlip.on_submit = on_submit
	SalarySlip.calculate_net_pay = calculate_net_pay
	SalarySlip.set_totals = set_totals
	SalarySlip.update_salary_slip_in_additional_salary = update_salary_slip_in_additional_salary
	SalarySlip.set_loan_repayment = set_loan_repayment
	SalarySlip.make_loan_repayment_entry = make_loan_repayment_entry
except :
	pass