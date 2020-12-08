from __future__ import unicode_literals
import frappe, erpnext
import datetime, math

from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words
from frappe.model.naming import make_autoname

from frappe import msgprint, _
from erpnext.hr.doctype.payroll_entry.payroll_entry import get_start_end_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils.background_jobs import enqueue
from erpnext.hr.doctype.additional_salary.additional_salary import get_additional_salary_component
from erpnext.hr.doctype.payroll_period.payroll_period import get_period_factor, get_payroll_period
from erpnext.hr.doctype.employee_benefit_application.employee_benefit_application import get_benefit_component_amount
from erpnext.hr.doctype.employee_benefit_claim.employee_benefit_claim import get_benefit_claim_amount, get_last_payroll_period_benefits


class MonthlySalarySlip(TransactionBase):
	def __init__(self, *args, **kwargs):
		super(MonthlySalarySlip, self).__init__(*args, **kwargs)
		self.series = 'Sal Slip/{0}/.#####'.format(self.employee)
		self.whitelisted_globals = {
			"int": int,
			"float": float,
			"long": int,
			"round": round,
			"date": datetime.date,
			"getdate": getdate
		}
		self.total_working_days_temp = 0
		self.daily_rate = 0

	def autoname(self):
		self.name = make_autoname(self.series)


	def validate(self):
		self.status = self.get_status()
		self.validate_dates()
		self.check_existing()
		self.check_sal_struct(self.start_date)

		# if not (len(self.get("earnings")) or len(self.get("deductions"))):
		# 	# get details from salary structure
		# 	self.get_emp_and_leave_details()
		# else:
		# 	self.get_leave_details(lwp = self.leave_without_pay)

	def validate_dates(self):
		if date_diff(self.end_date, self.start_date) < 0:
			frappe.throw(_("To date cannot be before From date"))

	def get_status(self):
		if self.docstatus == 0:
			status = "Draft"
		elif self.docstatus == 1:
			status = "Submitted"
		elif self.docstatus == 2:
			status = "Cancelled"
		return status


	def check_existing(self):
		if not self.salary_slip_based_on_timesheet:
			ret_exist = frappe.db.sql(""" SELECT name from `tabMonthly Salary Slip`
						where start_date ='%s' and end_date ='%s' and docstatus != 2
						and employee = '%s' and name != '%s' and payroll_type='%s' """%
						(self.start_date, self.end_date, self.employee, self.name ,self.payroll_type))
			if ret_exist:
				self.employee = ''
				frappe.throw(_("Salary Slip of employee {0} already created for this period").format(self.employee))
		else:
			for data in self.timesheets:
				if frappe.db.get_value('Timesheet', data.time_sheet, 'status') == 'Payrolled':
					frappe.throw(_("Salary Slip of employee {0} already created for time sheet {1}").format(self.employee, data.time_sheet))
	def get_emp_and_leave_details(self):
		'''First time, load all the components from salary structure'''

		if self.employee:
			self.set("earnings", [])
			self.set("deductions", [])
			self.validate_dates()
			joining_date, relieving_date = frappe.get_cached_value("Employee", self.employee,
				["date_of_joining", "relieving_date"])

			struct = self.check_sal_struct(joining_date, relieving_date)

			if struct:
				self._salary_structure_doc = frappe.get_doc('Salary Structure', struct)
				self.salary_slip_based_on_timesheet = self._salary_structure_doc.salary_slip_based_on_timesheet or 0
				self.set_time_sheet()
				self.pull_sal_struct()
				self.calculate_hour_rate()

			self.get_leave_details(joining_date, relieving_date)
			if struct :
				self.calculate_attendance()
				self.calculate_Tax()
				self.calculate_net_pay()


	def check_sal_struct(self, starting_date):


		salary_structure = frappe.db.sql(""" SELECT name FROM `tabMulti salary structure` WHERE  from_date  <=  '%s' """%starting_date)
		if not salary_structure :
			frappe.msgprint(_("No active or default Salary Structure found for employee {0} for the given dates")
				.format(self.employee), title=_('Salary Structure Missing'))
		else:

			pass



		# cond = """and sa.employee=%(employee)s and (sa.from_date <= %(start_date)s or
		# 		sa.from_date <= %(end_date)s or sa.from_date <= %(joining_date)s)"""
		# if self.payroll_frequency:
		# 	cond += """and ss.payroll_frequency = '%(payroll_frequency)s'""" % {"payroll_frequency": self.payroll_frequency}
		# st_name = frappe.db.sql("""
		# 	select sa.salary_structure
		# 	from `tabSalary Structure Assignment` sa join `tabSalary Structure` ss
		# 	where sa.salary_structure=ss.name
		# 		and sa.docstatus = 1 and ss.docstatus = 1 and ss.is_active ='Yes' %s
		# 	order by sa.from_date desc
		# 	limit 1
		# """ %cond, {'employee': self.employee, 'start_date': self.start_date,
		# 	'end_date': self.end_date, 'joining_date': joining_date})

		# if st_name:
		# 	self.salary_structure = st_name[0][0]
		# 	return self.salary_structure

		# else:
		# 	self.salary_structure = None
		# 	frappe.msgprint(_("No active or default Salary Structure found for employee {0} for the given dates")
		# 		.format(self.employee), title=_('Salary Structure Missing'))