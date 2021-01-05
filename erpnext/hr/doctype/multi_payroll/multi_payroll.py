# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import  datetime
from frappe.utils import cint, flt, nowdate, add_days, getdate, fmt_money, add_to_date, DATE_FORMAT, date_diff
from dateutil.relativedelta import relativedelta
from erpnext.accounts.utils import get_fiscal_year
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee

class MultiPayroll(Document):
	def fill_employee_details(self):
		self.set('employees', [])
		employees = self.get_emp_list()
		if not employees:
			frappe.throw(_("No employees for the mentioned criteria"))
	
		for d in employees:
			valid = validate_salary_slip(d[0],self. start_date , self.end_date ,self.payroll_type)
			if valid and  d[2] <= datetime.strptime( self.end_date, "%Y-%m-%d").date() :
				row  = self.append('employees', {})
				row.employee = d[0]
				row.salary_structure = d[1]
		self.number_of_employees = len(self.employees)
	def check_mandatory(self):
		for fieldname in ['company', 'start_date', 'end_date']:
			if not self.get(fieldname):
				frappe.throw(_("Please set {0}").format(self.meta.get_label(fieldname)))

	def get_filter_condition(self):
		self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'designation']:
			if self.get(f):
				cond += " and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		return cond

	def get_sal_slip_list(self, ss_status, as_dict=False):
		"""
			Returns list of salary slips based on selected criteria
		"""
		cond = self.get_filter_condition()

		ss_list = frappe.db.sql("""
			select t1.name, t1.salary_structure from `tabMonthly Salary Slip` t1
			where t1.docstatus = %s
			and t1.payroll_type = %s and t1.month = %s
			and (t1.journal_entry is null or t1.journal_entry = '')
			 and t1.company = '%s'
			 %s

		""" % ('%s', '%s', '%s', self.company, cond), (str(ss_status), str(self.payroll_type), str(self.payroll_month)),
								as_dict=as_dict)
		return ss_list

	def get_sal_slip_list_details(self, ss_status=1, as_dict=True):
		"""
			Returns list of salary slips based on selected criteria
		"""
		cond = self.get_filter_condition()

		ss_list = frappe.db.sql("""
			select t1.employee, t1.salary_structure , t1.total_deduction , t1.gross_pay , total_loan_repayment from `tabMonthly Salary Slip` t1
			where t1.docstatus = %s
			and t1.payroll_type = %s and t1.month = %s
			and (t1.journal_entry is null or t1.journal_entry = '')
			 and t1.company = '%s'
			 %s

		""" % ('%s', '%s', '%s', self.company, cond), (str(ss_status), str(self.payroll_type), str(self.payroll_month)),
								as_dict=as_dict)
		return ss_list

	def submit_salary_slips(self):
		self.check_permission('write')
		ss_list = self.get_sal_slip_list(ss_status=0)
		if len(ss_list) > 30:
			frappe.enqueue(submit_salary_slips_for_employees, timeout=600, payroll_entry=self, salary_slips=ss_list)
		else:
			submit_salary_slips_for_employees(self, ss_list, publish_progress=False)

	def get_emp_list(self):
		assignment = """SELECT  distinct t1.employee , t2.salary_structure  , em.date_of_joining , em.relieving_date
		 FROM `tabMulti salary structure` AS t1   join  `tabSalary structure Template` AS t2
		 ON t1.name = t2.parent 
		 join `tabEmployee` AS em on   t1.employee = em.name 
		 WHERE type = '%s' 
		 and t2.docstatus = 1 and t1.status='open' 
		 and em.company = '%s'
		 """%(self.payroll_type,self.company)

		if self.department : 
		 	department_con = """ and  t1.department = '%s'  """%self.department
		 	assignment += department_con
		# frappe.msgprint(assignment)
		self.employee_data = frappe.db.sql(assignment)
		try :
			data =[ i for i in self.employee_data ]
		except:
			data = None
		return  data
	
	def create_salary_slips(self ):
			if self.employees:
				self.salary_slips_created = 1
				for salary_structure in self.employees:
					# try:
						salary_slip_name = frappe.db.get_value('Monthly Salary Slip', {

							'payroll_type': self.payroll_type,
							'month': self.payroll_month,
							'employee': salary_structure.employee,
						}, ['name'])

						if not salary_slip_name:
							salary_slip = frappe.new_doc('Monthly Salary Slip')
							salary_slip.posting_date = datetime.today()
							salary_slip.employee = salary_structure.employee
							employe = frappe.get_doc("Employee", str(salary_structure.employee))
							salary_slip.month = self.payroll_month
							salary_slip.payroll_type = self.payroll_type
							salary_slip.start_date = self.start_date
							salary_slip.end_date = self.end_date
							salary_slip.save()
					# except Exception as e:
					# 	frappe.msgprint( str(e),title=_("Error in Employee {}'s Salary Slip"), indicator='red')
					# 	self.salary_slips_created = 0

			self.save()
			self.submit()
	def get_default_payroll_payable_account(self):
		payroll_payable_account = frappe.get_cached_value('Company',
			{"company_name": self.company},  "default_payroll_payable_account")

		if not payroll_payable_account:
			frappe.throw(_("Please set Default Payroll Payable Account in Company {0}")
				.format(self.company))

		return payroll_payable_account
	def get_loan_details(self):
		"""
			Get loan details from submitted salary slip based on selected criteria
		"""
		cond = self.get_filter_condition()
		return frappe.db.sql(""" select eld.loan_account, eld.loan,
				eld.interest_income_account, eld.principal_amount, eld.interest_amount, eld.total_payment,t1.employee
			from
				`tabSalary Slip` t1, `tabSalary Slip Loan` eld
			where
				t1.docstatus = 1 and t1.name = eld.parent and start_date >= %s and end_date <= %s %s
			""" % ('%s', '%s', cond), (self.start_date, self.end_date), as_dict=True) or []

	def make_accrual_jv_entry(self):
		self.check_permission('write')
		earnings = self.get_salary_component_total(component_type = "earnings") or {}
		deductions = self.get_salary_component_total(component_type = "deductions") or {}
		default_payroll_payable_account = self.get_default_payroll_payable_account()
		loan_details = self.get_loan_details()
		jv_name = ""
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		if earnings or deductions:
			journal_entry = frappe.new_doc('Journal Entry')
			journal_entry.voucher_type = 'Journal Entry'
			journal_entry.user_remark = _('Accrual Journal Entry for salaries from {0} to {1}').format(self.start_date, self.end_date)
			journal_entry.company = self.company
			journal_entry.posting_date = self.posting_date

			accounts = []
			payable_amount = 0

			# Earnings
			for acc, amount in earnings.items():
				payable_amount += flt(amount, precision)
				accounts.append({
						"account": acc,
						"debit_in_account_currency": flt(amount, precision),
						"party_type": '',
						"cost_center": self.cost_center,
						"project": self.project
					})

			# Deductions
			for acc, amount in deductions.items():
				payable_amount -= flt(amount, precision)
				accounts.append({
						"account": acc,
						"credit_in_account_currency": flt(amount, precision),
						"cost_center": self.cost_center,
						"party_type": '',
						"project": self.project
					})

			# Loan
			for data in loan_details:
				accounts.append({
						"account": data.loan_account,
						"credit_in_account_currency": data.principal_amount,
						"party_type": "Employee",
						"party": data.employee
					})

				if data.interest_amount and not data.interest_income_account:
					frappe.throw(_("Select interest income account in loan {0}").format(data.loan))

				if data.interest_income_account and data.interest_amount:
					accounts.append({
						"account": data.interest_income_account,
						"credit_in_account_currency": data.interest_amount,
						"cost_center": self.cost_center,
						"project": self.project,
						"party_type": "Employee",
						"party": data.employee
					})
				payable_amount -= flt(data.total_payment, precision)
			employees_dict = self.get_sal_slip_list_details()

			for i in employees_dict:
				accounts.append({
					"account": default_payroll_payable_account,
					"party_type": "Employee",
					"party": i.employee,
					"credit_in_account_currency": flt(i.gross_pay),
					"cost_center": self.cost_center,
					"project": self.project
				})
				accounts.append({
					"account": default_payroll_payable_account,
					"party_type": "Employee",
					"party": i.employee,
					"debit_in_account_currency": flt(i.total_deduction),
					"cost_center": self.cost_center,
					"project": self.project
				})
				if i.total_loan_repayment:
					accounts.append({
						"account": default_payroll_payable_account,
						"party_type": "Employee",
						"party": i.employee,
						"debit_in_account_currency": flt(i.total_loan_repayment),
						"cost_center": self.cost_center,
						"project": self.project
					})

			# Payable amount
			# accounts.append({
			# 	"account": default_payroll_payable_account,
			# 	"credit_in_account_currency": flt(payable_amount, precision),
			# 	"party_type": '',
			# 	"cost_center": self.cost_center
			# })

			journal_entry.set("accounts", accounts)
			journal_entry.title = default_payroll_payable_account
			journal_entry.save()

			try:
				journal_entry.submit()
				jv_name = journal_entry.name
				self.update_salary_slip_status(jv_name = jv_name)
			except Exception as e:
				frappe.msgprint(str(e))

		return jv_name
	def email_salary_slip(self, submitted_ss):
		if frappe.db.get_single_value("HR Settings", "email_salary_slip_to_employee"):
			for ss in submitted_ss:
				ss.email_salary_slip()
	def update_salary_slip_status(self, jv_name = None):
		ss_list = self.get_sal_slip_list(ss_status=1)
		for ss in ss_list:
			ss_obj = frappe.get_doc("Monthly Salary Slip",ss[0])
			frappe.db.set_value("Monthly Salary Slip", ss_obj.name, "journal_entry", jv_name)

	def get_salary_component_account(self, salary_component):
		account = frappe.db.get_value("Salary Component Account",
			{"parent": salary_component, "company": self.company}, "default_account")

		if not account:
			frappe.throw(_("Please set default account in Salary Component {0}")
				.format(salary_component))

		return account
	def get_account(self, component_dict = None):
		account_dict = {}
		for s, a in component_dict.items():
			account = self.get_salary_component_account(s)
			account_dict[account] = account_dict.get(account, 0) + a
		return account_dict
	def make_payment_entry(self):
		self.check_permission('write')

		cond = self.get_filter_condition()

		salary_slip_name_list = frappe.db.sql(""" select t1.name from `tabMonthly Salary Slip` t1
			where t1.docstatus = 1 and t1.month = %s and t1.payroll_type = %s  and t1.company = '%s'
			%s
			""" % ('%s', '%s', self.company,cond), (self.payroll_month, self.payroll_type), as_list = True)
		# frappe.msgprint(str(salary_slip_name_list))
		if salary_slip_name_list and len(salary_slip_name_list) > 0:
			salary_slip_total = 0
			employee_salaries = []
			for salary_slip_name in salary_slip_name_list:
				salary_slip = frappe.get_doc("Monthly Salary Slip", salary_slip_name[0])
				for sal_detail in salary_slip.earnings:
					is_flexible_benefit, only_tax_impact, creat_separate_je, statistical_component = frappe.db.get_value("Salary Component", sal_detail.salary_component,
						['is_flexible_benefit', 'only_tax_impact', 'create_separate_payment_entry_against_benefit_claim', 'statistical_component'])
					if only_tax_impact != 1 and statistical_component != 1:
						# if is_flexible_benefit == 1 and creat_separate_je == 1:
						# 	self.create_journal_entry(sal_detail.amount, sal_detail.salary_component)
						# else:
							salary_slip_total += sal_detail.amount
				for sal_detail in salary_slip.deductions:
					statistical_component = frappe.db.get_value("Salary Component", sal_detail.salary_component, 'statistical_component')
					if statistical_component != 1:
						salary_slip_total -= sal_detail.amount

				#loan deduction from bank entry during payroll
				salary_slip_total -= salary_slip.total_loan_repayment
				employee_salaries.append(frappe._dict({"employee":salary_slip.employee, "amount" : flt(salary_slip.net_pay)}))

			if salary_slip_total > 0:
				self.create_journal_entry(salary_slip_total, "salary" ,employee_salaries)
	def create_journal_entry(self, je_payment_amount, user_remark , employee_salaries = None):
		default_payroll_payable_account = self.get_default_payroll_payable_account()
		precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

		journal_entry = frappe.new_doc('Journal Entry')
		journal_entry.voucher_type = 'Bank Entry'
		journal_entry.user_remark = _('Payment of {0} from {1} to {2}')\
			.format(user_remark, self.start_date, self.end_date)
		journal_entry.company = self.company
		journal_entry.posting_date = self.posting_date

		payment_amount = flt(je_payment_amount, precision)
		accounts = [
			{
				"account": self.payment_account,
				"bank_account": self.bank_account,
				"credit_in_account_currency": payment_amount
			}
			# ,
			# {
			# 	"account": default_payroll_payable_account,
			# 	"debit_in_account_currency": payment_amount,
			# 	"reference_type": self.doctype,
			# 	"reference_name": self.name
			# }
		]
		if employee_salaries:
			for i in employee_salaries :
				accounts.append({
					"account": default_payroll_payable_account,
					"debit_in_account_currency": i.amount,
					"party_type": "Employee",
					"party": i.employee,
					"reference_type": self.doctype,
					"reference_name": self.name
				})
			
		else :
			accounts.append({
				"account": default_payroll_payable_account,
				"debit_in_account_currency": payment_amount,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"party_type": self.doctype,
				"party": self.name
			})
		journal_entry.set("accounts", accounts)
		journal_entry.save(ignore_permissions = True)

	def calculate_salary_slip (self):
			if self.employees:
				for employee in self.employees :
					salary_slip_name = frappe.db.get_value('Monthly Salary Slip' , {

						'payroll_type' : self.payroll_type,
						'month':self.payroll_month ,
						'employee': employee.employee,
					} , 'name' )

					if salary_slip_name :
						salary_slip = frappe.get_doc('Monthly Salary Slip' ,salary_slip_name )
						if salary_slip.docstatus == 0:
							salary_slip.run_method('get_Employee_Salary_Details')
							salary_slip.save()
						else :
							frappe.msgprint(_("Salary Slip {} Has been Submitted ".format(salary_slip.name)))
			frappe.msgprint(_("Done"))
	def get_salary_components(self, component_type):
		salary_slips = self.get_sal_slip_list(ss_status = 1, as_dict = True)
		if salary_slips:
			salary_components = frappe.db.sql("""select salary_component, amount, parentfield
				from `tabSalary Detail` where parentfield = '%s' and parent in (%s)""" %
				(component_type, ', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=True)
			return salary_components

	def get_salary_component_total(self, component_type = None):
		salary_components = self.get_salary_components(component_type)
		if salary_components:
			component_dict = {}
			for item in salary_components:
				add_component_to_accrual_jv_entry = True
				if component_type == "earnings":
					is_flexible_benefit, only_tax_impact = frappe.db.get_value("Salary Component", item['salary_component'], ['is_flexible_benefit', 'only_tax_impact'])
					if is_flexible_benefit == 1 and only_tax_impact ==1:
						add_component_to_accrual_jv_entry = False
				if add_component_to_accrual_jv_entry:
					component_dict[item['salary_component']] = component_dict.get(item['salary_component'], 0) + item['amount']
			account_details = self.get_account(component_dict = component_dict)
			return account_details


	def get_joining_relieving_condition(self):
		cond = """
			and ifnull(t1.date_of_joining, '0000-00-00') <= '%(end_date)s'
			and ifnull(t1.relieving_date, '2199-12-31') >= '%(start_date)s'
		""" % {"start_date": self.start_date, "end_date": self.end_date}
		return cond

def get_employee_attendence_rule(emp):
	emplpyee = frappe.get_doc("Employee" ,emp)


@frappe.whitelist()
def create_salary_slips_for_employees(employees, args, publish_progress=True):
	salary_slips_exists_for = get_existing_salary_slips(employees, args)
	count=0
	for emp in employees:
		if emp not in salary_slips_exists_for:
			args.update({
				"doctype": "Monthly Salary Slip",
				"employee": emp
			})
			ss = frappe.get_doc(args)
			ss.insert()
			count+=1
			if publish_progress:
				frappe.publish_progress(count*100/len(set(employees) - set(salary_slips_exists_for)),
					title = _("Creating Salary Slips..."))

	payroll_entry = frappe.get_doc("Payroll Entry", args.payroll_entry)
	payroll_entry.db_set("salary_slips_created", 1)
	payroll_entry.notify_update()

def submit_salary_slips_for_employees(payroll_entry, salary_slips, publish_progress=True):
	submitted_ss = []
	not_submitted_ss = []
	frappe.flags.via_payroll_entry = True

	count = 0
	for ss in salary_slips:
		ss_obj = frappe.get_doc("Monthly Salary Slip",ss[0])
		# frappe.msgprint(str(ss_obj))
		if ss_obj.net_pay<0:
			not_submitted_ss.append(ss[0])
		else:
			try:
				ss_obj.submit()
				submitted_ss.append(ss_obj)
			except frappe.ValidationError as e:
				frappe.msgprint(str(e))
				not_submitted_ss.append(ss[0])

		count += 1
		if publish_progress:
			frappe.publish_progress(count*100/len(salary_slips), title = _("Submitting Salary Slips..."))
	if submitted_ss:
		payroll_entry.make_accrual_jv_entry()
		frappe.msgprint(_("Salary Slip submitted for period from {0} to {1}")
			.format(ss_obj.start_date, ss_obj.end_date))

		payroll_entry.email_salary_slip(submitted_ss)

		payroll_entry.db_set("salary_slips_submitted", 1)
		payroll_entry.notify_update()

	if not submitted_ss and not not_submitted_ss:
		frappe.msgprint(_("No salary slip found to submit for the above selected criteria OR salary slip already submitted"))

	if not_submitted_ss:
		frappe.msgprint(_("Could not submit some Salary Slips"))


@frappe.whitelist()
def find_global_company():
	company = frappe.db.get_single_value("Global Defaults" ,"default_company")
	return(company)

def get_existing_salary_slips(employees, args):
	return frappe.db.sql_list("""
		select distinct employee from `tabSalary Slip`
		where docstatus!= 2 and company = %s
			and start_date >= %s and end_date <= %s
			and employee in (%s) and payroll_type
	""" % ('%s', '%s', '%s', ', '.join(['%s']*len(employees))),
		[args.company, args.start_date, args.end_date ,args.payroll_type] + employees)


def validate_salary_slip(employee ,  start_date,end_date,payroll_type):
	data = frappe.db.sql(""" SELECT name FROM `tabSalary Slip` WHERE  employee ='%s' and docstatus!= 2 and  start_date = '%s' AND  
		end_date = '%s' and  payroll_type='%s'  """%(employee ,  start_date,end_date,payroll_type))
	try :
		if len(data) > 0 :
			return False
		else:
			return True
	except:
		return True

@frappe.whitelist()
def payroll_entry_has_bank_entries(name):
	response = {}
	bank_entries = get_payroll_entry_bank_entries(name)
	response['submitted'] = 1 if bank_entries else 0

	return response

def get_payroll_entry_bank_entries(payroll_entry_name):
	journal_entries = frappe.db.sql(
		'select name from `tabJournal Entry Account` '
		'where reference_type="Multi Payroll" '
		'and reference_name=%s and docstatus=1',
		payroll_entry_name,
		as_dict=1
	)

	return journal_entries