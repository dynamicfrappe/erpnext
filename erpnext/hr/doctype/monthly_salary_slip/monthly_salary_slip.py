from __future__ import unicode_literals
import frappe, erpnext
import datetime, math
from frappe import _
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words
from frappe.model.naming import make_autoname

from frappe import msgprint, _
from erpnext.hr.doctype.payroll_entry.payroll_entry import get_start_end_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils.background_jobs import enqueue
from erpnext.hr.doctype.additional_salary.additional_salary import get_additional_salary_component
from erpnext.hr.doctype.additional_salary.additional_salary import get_additional_salary_component_with_salary_component
from erpnext.hr.doctype.payroll_period.payroll_period import get_period_factor, get_payroll_period
from erpnext.hr.doctype.employee_benefit_application.employee_benefit_application import get_benefit_component_amount
from erpnext.hr.doctype.employee_benefit_claim.employee_benefit_claim import get_benefit_claim_amount, get_last_payroll_period_benefits





employee_status = {"""  Present
						Absent
						Leave
						Holiday
						Business Trip
						Mission
						Mission All Day"""}
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
		self.real_month = None
		self.salary_slip_based_on_timesheet = None
		# self.total_working_days = 0  
	def autoname(self):
		self.name = make_autoname(self.series)

	def set_dates_above_month(self):
		if self.month :
			real_month = frappe.get_doc("Payroll Month" ,self.month)
			if not real_month.is_closed:
				self.start_date = real_month.start_date
				self.end_date = real_month.end_date

			else :
				frappe.throw("You Chosed Closed Month ")

		else: 
			frappe.throw("Pleas Set financial Month First !")
	def validate(self):
		self.get_active_month()
		self.total_working_days= self.get_monthly_working_days_from_attendence_rule()
		self.status = self.get_status()
		self.validate_dates()
		self.check_existing()
		self.set_salary_component_first_time()
		self.ceck_for_update_values_in_salary_strycrtue()
		self.set_formula_valus()
		self.update_dates_for_employee()


	def validate_dates(self):
		if date_diff(self.end_date, self.start_date) < 0:
			frappe.throw(_("To date cannot be before From date"))




	def get_active_salary_structure (self):
		active_salary = frappe.db.sql(""" SELECT name FROM `tabMulti salary structure` WHERE employee = '%s' AND from_date <= '%s'
		 AND docstatus= 1 """%(self.employee ,  self.end_date ))
		return active_salary


	def get_employee_active_salary_structure_type(self):
		active_salary =self.get_active_salary_structure()
		if active_salary :
			valid_types = frappe.db.sql(""" SELECT type FROM `tabSalary structure Template` WHERE parent = '%s'
			 """%(str(active_salary[0][0])))
			return([x for x in valid_types[0]])
 
		else :
			frappe.throw("No Active Salary Structure For employee '%s' , from date '%s' "%(self.employee , self.start_date))

	def get_monthly_working_days_from_attendence_rule(self):
		get_data =  frappe.db.sql("""SELECT  a.total_working_days_per_month FROM `tabEmployee` AS e 
			JOIN `tabAttendance Rule` AS a 
			ON e.attendance_role = a.name 
			WHERE e.name = '%s' """%self.employee )
		try :
			return get_data[0][0]
		except:
			frappe.throw(_("Please Set working days in Employee Attendence Rule"))
	def get_active_month(self):
		active_month = frappe.get_doc("Payroll Month" ,self.month)
		start = active_month.start_date
		end = active_month.end_date
		if (start == self.start_date and  end == self.end_date) :
			self.payment_days = self.total_working_days
		else :
			self.payment_days = date_diff(self.end_date , self.start_date)

	def get_amount_pase_on_formula(self,formula , data = None):
		data = { i.abbr:i.amount  for i in self.earnings}
		func  =formula.strip(" ").replace("\n", " ")
		d =[i for  i in data.keys() ]
		for e in range(0,len(d)) :
			func  = func.replace(str(max(d ,key=len)) , str(data[max(d ,key=len)]))
			d.remove(max(d ,key=len))
			
		try :
			return (eval(func))
		except:
			return("error")
		

	def set_salary_component_first_time(self):
		active_salary =self.get_active_salary_structure()
		stucture_name = frappe.db.sql("""SELECT salary_structure FROM `tabSalary structure Template` WHERE parent='%s' and type='%s'  
			    """%(active_salary[0][0] ,self.payroll_type))


		salary_component = frappe.get_doc("Salary Structure" ,stucture_name[0][0] )
		self.set('earnings',[])
		for i in salary_component.earnings  :
					self.set_component(i , 'earnings')
		self.set('deductions',[])
		for i in salary_component.deductions :
					self.set_component(i , 'deductions')
	def get_attendance (self):
		component_list = frappe.db.sql("""SELECT  
												a.fingerprint_forgetten_penlaity_salary_component,
												a.salary_componat_for_late,
												a.salary_component_for_late_penalty	,
												a.absent__component,
												a.abset_penalty_component,
												a.overtime_salary_component,
												a.staying_up_late_salary_component,
												a.overtime_in_holiday_salary_component,
												a.overtime_in_weekend_salary_component,
												a.less_time_salary_component
												 FROM `tabEmployee` AS e 
													JOIN `tabAttendance Rule` AS a 
													ON e.attendance_role = a.name 
													WHERE e.name = '%s' """%self.employee ) [0] or None
		if component_list:
			attendance_earnings = get_additional_salary_component_with_salary_component(self.employee , self.start_date,self.end_date , "earnings" , component_list)
			if attendance_earnings:
				self.add_attendance_additional_salary_components ("earnings",attendance_earnings)

			attendance_deductions = get_additional_salary_component_with_salary_component(self.employee , self.start_date,self.end_date , "deductions" , component_list)
			if attendance_deductions:
				self.add_attendance_additional_salary_components ("deductions",attendance_deductions)

	def add_attendance_additional_salary_components(self, component_type , additional_components):

		if additional_components:
			for additional_component in additional_components:
				amount = additional_component.amount
				overwrite = additional_component.overwrite
				self.update_component_row(frappe._dict(additional_component.struct_row), amount,
					component_type, overwrite=overwrite)

	def update_dates_for_employee(self):
		employe = frappe.get_doc("Employee" ,str(self.employee) )
		if employe.date_of_joining <= datetime.datetime.strptime( self.start_date, "%Y-%m-%d").date():
			pass
		else:
			self.start_date=employe.date_of_joining
		if 	 employe.relieving_date :
			if employe.relieving_date  >= datetime.strptime( self.end_date, "%Y-%m-%d").date():
				pass
			else:
				self.end_date =employe.relieving_date
		

	def ceck_for_update_values_in_salary_strycrtue(self):
	
		for i in self.earnings :
			new_value = self.get_updated_value(i.salary_component)
			if new_value :
				i.amount = float(new_value)
		for i in self.deductions:
			new_value = self.get_updated_value(i.salary_component)
			if new_value :
				i.amount = float(new_value)



	def set_formula_valus(self):

		for i in self.earnings :
			if i.amount_based_on_formula :

				i.amount = self.get_amount_pase_on_formula(i.formula)
				
		for i in self.deductions:
			if i.amount_based_on_formula :
				i.amount = self.get_amount_pase_on_formula(i.formula)

		# for i in self.earnings :
		# 	value = frappe.db.sql(""" SELECT amount FROM `tabSalary Detail` WHERE parent ='%s' and
		# 		abbr = '%s' """ %(str(salary_structure[0][1]) , i.component_short_name))
		# 	if value :
		# 		data[str(i.component_short_name)] = float(value[0][0])
		# 	else :
		# 		data[str(i.component_short_name)] = 0
		# 		# frappe.throw("Validation error in component '%s' pleas check if employee have it in his salary struct "%i.component_short_name)

		
		# formula = component.formula
		# if formula :
		# 	return self.get_amount_pase_on_formula(formula ,data)
		# else :
		# 	return 0 

	def get_updated_value(self , i):
		active_salary =self.get_active_salary_structure()
		value = frappe.db.sql("""SELECT amount from `tabSalary Components` WHERE parent ='%s' AND componentname = '%s' 
			"""%(active_salary[0][0] , i))

		if value:
			if (float(value[0][0])) > 0  :
				return(value[0][0])
			else:
				return False

	def set_component(self,i,typ):
		
		if i.amount >= 0 :	
				row = self.append(typ, {})
				row.salary_component = i.salary_component
				row.abbr= i.abbr
				row.statistical_component = i.statistical_component
				row.deduct_full_tax_on_selected_payroll_date = i.deduct_full_tax_on_selected_payroll_date
				row.depends_on_payment_days =i.depends_on_payment_days
				row.is_tax_applicable = i.is_tax_applicable
				row.exempted_from_income_tax = i.exempted_from_income_tax
				row.amount_based_on_formula = i.amount_based_on_formula
				row.formula = i.formula
				row.amount = i.amount
				

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
				# self.calculate_attendance()
				self.calculate_Tax()
				self.calculate_net_pay()

	def calculate_Tax(self):
		total_taxable_amount = 0
		for e in self.get("earnings"):
			SC = frappe.get_doc("Salary Component", e.salary_component)
			if SC:
				if not SC.exempted_from_income_tax:
					total_taxable_amount += e.amount
		for e in self.get("deductions"):
			SC = frappe.get_doc("Salary Component", e.salary_component)
			if SC:
				if not SC.exempted_from_income_tax:
					total_taxable_amount -= e.amount
		self.tax_pool = total_taxable_amount or 0
		self.Tax_calculated = 0

		if self.calculate_income_tax:
			total_tax_pool = frappe.db.sql("""
			select ifnull(sum(tax_pool),0) from `tabMonthly Salary Slip`
			where employee = '{employee}' and calculate_income_tax = 0 and month = '{month}' and tax_calculated = 0 """.format(
				month=self.month, employee=self.employee))[0][0]
			total_taxable_amount += total_tax_pool
			hr_settings = frappe.get_single("HR Settings")
			Tax_Sc = hr_settings.income_tax_salary_component or None
			personal_exemption_value = hr_settings.personal_exemption_value or 0
			disability_exemption_value = hr_settings.disability_exemption_value or 0
			tax_layers = hr_settings.tax_layers or None
			if Tax_Sc and tax_layers:

				if total_taxable_amount:
					total_taxable_amount_yearly = (total_taxable_amount * 12) - personal_exemption_value
					total_tax = 0
					perviuos_limit = 0
					number = str(int(total_taxable_amount_yearly))[:-1]
					number = number + str('0')
					total_taxable_amount_yearly = float(number)
					for i in tax_layers:
						if i.limit < total_taxable_amount_yearly:
							total_tax += (i.limit - perviuos_limit) * (i.tax_percent / 100)
							perviuos_limit = i.limit


						else:
							total_taxable_amount_yearly -= perviuos_limit
							total_tax += total_taxable_amount_yearly * (i.tax_percent / 100)
							break;
					total_tax = total_tax / 12
					if total_tax:
						row = self.get_salary_slip_row(Tax_Sc)

						self.update_component_row(row, total_tax, "deductions", adding=1)
			self.tax_calculated = 1
			frappe.db.sql("""update  `tabMonthly Salary Slip`
						set tax_calculated = 1
						where employee = '{employee}' and calculate_income_tax = 0 and month = '{month}' and tax_calculated = 0""".format(
				month=self.month, employee=self.employee))
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
	def update_component_row(self, struct_row, amount, key, overwrite=1 , adding = 0):
		component_row = None
		for d in self.get(key):
			if d.salary_component == struct_row.salary_component:
				component_row = d

		if not component_row:
			if amount:
				self.append(key, {
					'amount': amount,
					'default_amount': amount if not struct_row.get("is_additional_component") else 0,
					'depends_on_payment_days' : struct_row.depends_on_payment_days,
					'salary_component' : struct_row.salary_component,
					'abbr' : struct_row.abbr,
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
				else:
					component_row.additional_amount = amount

				if not overwrite and component_row.default_amount:
					amount += component_row.default_amount
			else:
				component_row.default_amount = amount

			if adding:
				component_row.amount += amount
			else :
				component_row.amount = amount
			component_row.deduct_full_tax_on_selected_payroll_date = struct_row.deduct_full_tax_on_selected_payroll_date

	def check_sal_struct(self, starting_date):


		salary_structure = frappe.db.sql(""" SELECT name FROM `tabMulti salary structure` WHERE  from_date  <=  '%s' 
		 and status='open' """%starting_date)
		if not salary_structure :
			frappe.msgprint(_("No active or default Salary Structure found for employee {0} for the given dates")
				.format(self.employee), title=_('Salary Structure Missing'))
		else:

			pass


