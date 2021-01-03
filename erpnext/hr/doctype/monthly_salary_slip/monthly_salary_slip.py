from __future__ import unicode_literals
import frappe, erpnext
import datetime, math

from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words
from frappe.model.naming import make_autoname

from frappe import msgprint, _
from erpnext.hr.doctype.payroll_entry.payroll_entry import get_start_end_dates
from erpnext.hr.doctype.payroll_entry.payroll_entry import PayrollEntry
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
						Mission All Day
				"""}
class MonthlySalarySlip(TransactionBase):
	def __init__(self, *args, **kwargs):

		super(MonthlySalarySlip, self).__init__(*args, **kwargs)
		self.series = 'Sal Slip/{0}/.#####'.format(self.employee)
		self.social_insurance_amount = 0
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
		# self.total_working_days = self.get_monthly_working_days_from_attendence_rule()

	def autoname(self):
		self.series = 'Sal Slip/{0}/.#####'.format(self.employee)
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
		self.validate_dates()
		self.get_Employee_Salary_Details()

	def get_Employee_Salary_Details(self):
		# frappe.msgprint(str(self.is_main))

		self.get_employee_active_salary_structure_type()
		self.total_working_days = self.get_monthly_working_days_from_attendence_rule()
		self.get_active_month()

		self.status = self.get_status()


		self.check_existing()
		# self.check_sal_struct(self.end_date)
		self.set_salary_component_first_time()
		self.ceck_for_update_values_in_salary_strycrtue()
		self.set_formula_valus()
		self.update_dates_for_employee()
		self.get_absent_days()
		self.get_attendance()
		self.calculate_hour_rate()
		self.set_loan_repayment()
		if self.is_main:
			self.get_Employee_advance()
			self.get_medical_insurance()
			self.get_social_insurance()
			self.check_employee_leave_without_pay()
		self.calculate_Tax()
		self.calculate_net_pay()
		# self.check_employee_leave_without_pay()


	def validate_dates(self):
		if date_diff(self.end_date, self.start_date) < 0:
			frappe.throw(_("To date cannot be before From date"))

	def get_medical_insurance(self):

		amount = frappe.db.sql("""
				select ifnull(sum(total_document_fee_monthly),0)  as total_fee from `tabEmployee Medical Insurance Document` where docstatus=1   and employee = '{employee}' and status = 'Active'
				and date(insurance_document_start_date) <=   date('{end_date}')
				order  by insurance_document_start_date desc limit 1
				""".format(employee=self.employee ,end_date=self.end_date))[0][0] or 0

		if amount:
			salary_component = frappe.db.get_single_value("HR Settings", 'medical_insurance_salary_component')
			if salary_component:
				row = self.get_salary_slip_row(salary_component)

				self.update_component_row(row, amount, "deductions", adding=1, adding_if_not_exist=1)
	def get_social_insurance(self):

		data  = frappe.db.sql("""
				select  ifnull(sum(insurance_salary),0)  as insurance_salary , ifnull(is_owner,0) as is_owner from `tabEmployee Social Insurance Data`
				where docstatus = 1 and date(employee_strat_insurance_date) <= date('{end_date}') and  employee = '{employee}'
				""".format(employee=self.employee ,end_date=self.end_date))
		insurance_salary = data [0][0] or 0
		is_owner = data [0][1] or 0
		percent = 0
		if is_owner:
			percent = frappe.db.get_single_value("Social Insurance Settings", 'owner_percent') or 0
		else:
			percent = frappe.db.get_single_value("Social Insurance Settings", 'employee_percent') or 0


		amount = (insurance_salary * percent /100) or 0
		self.social_insurance_amount = amount or 0

		if amount:
			salary_component = frappe.db.get_single_value("Social Insurance Settings", 'social_insurance_salary_component')
			if salary_component:
				row = self.get_salary_slip_row(salary_component)

				self.update_component_row(row, amount, "deductions", adding=1, adding_if_not_exist=1)

	def get_Employee_advance(self):
		amount = frappe.db.sql("""
		select ifnull(SUM(case when (paid_amount - claimed_amount) >0 then (paid_amount - claimed_amount) else 0 end ),0) as advance from `tabEmployee Advance`
		where repay_unclaimed_amount_from_salary=1 and  docstatus = 1 and  employee = '{employee}' 
		""".format(employee=self.employee ))[0][0] or 0

		if amount:
			salary_component = frappe.db.get_single_value("HR Settings",'advance_salary_component')
			if salary_component :
				row = self.get_salary_slip_row(salary_component)

				self.update_component_row(row, amount, "deductions", adding=1, adding_if_not_exist=1)




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
		try:
			return get_data[0][0]
		except:
			frappe.throw(_("Please Set Toal Working Days per Month in Attendance Rule"))
	def get_active_month(self):
		active_month = frappe.get_doc("Payroll Month" ,self.month)
		start = active_month.start_date
		end = active_month.end_date
		if (start == self.start_date and  end == self.end_date) :
			self.payment_days = self.total_working_days

		else :
			self.payment_days = date_diff(self.end_date , self.start_date) +1


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

			return 0
		

	def set_salary_component_first_time(self):
		active_salary =self.get_active_salary_structure()
		stucture_name = frappe.db.sql("""SELECT salary_structure FROM `tabSalary structure Template` WHERE parent='%s' and type='%s'  
			    """%(active_salary[0][0] ,self.payroll_type))
		self.set('earnings', [])
		self.set('deductions', [])
		self.earnings = []
		self.deductions = []
		if stucture_name:
			salary_component = frappe.get_doc("Salary Structure" ,stucture_name[0][0] )

			for i in salary_component.earnings  :

						self.set_component(i , 'earnings')

			for i in salary_component.deductions :
						self.set_component(i , 'deductions')
		else :
			frappe.msgprint(_("No Active Salary Structure For employee '%s' , from date '%s' with this type '%s' "%(self.employee , self.start_date , self.payroll_type)) , raise_exception=0 , indicator='red')


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
		if employe.date_of_joining <= datetime.datetime.strptime( str(self.start_date), "%Y-%m-%d").date():
			pass
		else:
			self.start_date=employe.date_of_joining
		if 	 employe.relieving_date :
			if employe.relieving_date  >= datetime.strptime( str(self.end_date), "%Y-%m-%d").date():
				pass
			else:
				self.end_date =employe.relieving_date
	def get_absent_days (self):
		self.absent_days = frappe.db.sql("""
		select ifnull( SUM(case when type ="Absent" then 1 else 0  end) ,0) as absent_days from `tabEmployee Attendance Logs`
		where employee = '{employee}' and date(date) between date('{start_date}') and date('{end_date}')
		""".format(employee = self.employee,start_date = self.start_date , end_date = self.end_date),as_dict=1)[0].absent_days or 0


		

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
				return float(value[0][0])
		return 0

	def set_component(self,i,typ):
		# self.set(typ,[])

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
				# self.calculate_Tax()
				self.calculate_net_pay()

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
		has_disability , is_consultant = frappe.db.get_value("Employee" , self.employee , ['has_disability','is_consultant'])
		total_tax = 0
		hr_settings = frappe.get_single("HR Settings")
		Tax_Sc = hr_settings.income_tax_salary_component or None
		personal_exemption_value = hr_settings.personal_exemption_value or 0
		disability_exemption_value = hr_settings.disability_exemption_value or 0

		if is_consultant :
			consultant_percent = hr_settings.consultant_percent
			total_tax = total_taxable_amount * consultant_percent /100
		else :
			total_tax_pool = frappe.db.sql("""
			select ifnull(sum(tax_pool),0) from `tabMonthly Salary Slip`
			where employee = '{employee}'  and month = '{month}' and name <> '{name}' """.format(
				month=self.month, employee=self.employee , name=self.name))[0][0] or 0
			total_taxable_amount += total_tax_pool




			if has_disability :
				personal_exemption_value += disability_exemption_value

			tax_layers = hr_settings.tax_layers or None

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
					select ifnull(sum(tax_value),0) from `tabMonthly Salary Slip`
					where employee = '{employee}'  and month = '{month}' and name <> '{name}' """.format(
			month=self.month, employee=self.employee, name=self.name))[0][0] or 0
		total_tax -= total_tax_value
		if total_tax < 0:
			total_tax = 0

		self.tax_value = total_tax or 0
		if total_tax:
					row = self.get_salary_slip_row(Tax_Sc)

					self.update_component_row(row, total_tax, "deductions", adding=1,adding_if_not_exist=1)

	def calculate_hour_rate(self):


			total_hourly_salary = 0
			for item in self.get("earnings"): #if not (len(self.get("earnings")) or len(self.get("deductions"))):
				salary_compnent = frappe.get_doc("Salary Component" , item.salary_component)
				if salary_compnent :
					if salary_compnent.consider_in_hour_rate and salary_compnent.type == "Earning" and  item.amount:
						# frappe.msgprint(str(item.amount))
						total_hourly_salary += item.amount
			total_working_days = self.total_working_days
			attendance_rule = frappe.db.get_value("Employee" , self.employee , "attendance_role")
			if attendance_rule:
				attendance_rule = frappe.get_doc("Attendance Rule" , attendance_rule)

				if self.payroll_frequency == "Monthly":
					total_working_days = attendance_rule.total_working_days_per_month or self.total_working_days or 0
				total_working_hours_per_day = attendance_rule.total_working_hours_per_day or 0
				if not total_working_hours_per_day:
						frappe.msgprint(
							_("Please Set The Total Working Hours for Employee {} in Attendance Rule".format(self.employee)), title='Error', indicator='red',
							raise_exception=1)
				self.hour_rate = total_hourly_salary / (total_working_hours_per_day * total_working_days)
				self.total_working_days_temp = total_working_days
				self.daily_rate = total_hourly_salary / (total_working_days)

			# frappe.msgprint('total_hourly_salary')
			# frappe.msgprint(str(total_hourly_salary))
			# frappe.msgprint('total_working_hours_per_day')
			# frappe.msgprint(str(total_working_hours_per_day))
			# frappe.msgprint('total_working_days')
			# frappe.msgprint(str(total_working_days))
			# frappe.msgprint('str(self.hour_rate)')
			# frappe.msgprint(str(self.hour_rate))




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
	def update_component_row(self, struct_row, amount, key, overwrite=1 , adding = 0 , adding_if_not_exist = 0):
		component_row = None
		for d in self.get(key):
			if d.salary_component == struct_row.salary_component:
				component_row = d

		if not component_row:
			if adding_if_not_exist :
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


	def check_employee_leave_without_pay(self):
		self.leave_without_pay = 0
		month_leave = frappe.db.sql(""" SELECT total_leave_days FROM `tabLeave Application`  WHERE employee='%s' 
			and leave_type='Leave Without Pay' and 
			from_date >= '%s' and to_date <= '%s' """%(self.employee , self.start_date,self.end_date))
		if month_leave :
			self.leave_without_pay = int(month_leave[0][0])
			
		get_end_month_leaves = frappe.db.sql(""" SELECT total_leave_days ,to_date FROM `tabLeave Application`  WHERE employee='%s' 
			and leave_type='Leave Without Pay' and 
			from_date <= '%s' and to_date >= '%s' """%(self.employee , self.end_date,self.end_date))
		
		if get_end_month_leaves :
			defrence_between_end =  date_diff( self.end_date,get_end_month_leaves[0][1] )
			end_month_dates = int(get_end_month_leaves[0][0]) + defrence_between_end
			self.leave_without_pay += end_month_dates

			# self.payment_days = self.payment_days-self.leave_without_pay
		self.payment_days = self.payment_days - self.leave_without_pay
		if self.leave_without_pay :
			amount = self.leave_without_pay * self.daily_rate or 0
			sc = frappe.db.get_single_value("HR Settings","leave_without_pay_salary_component")
			if not sc :
				frappe.throw(_("Please Set Leave Without Pay Salary Component In Hr Settings"))
			if amount :
				row = self.get_salary_slip_row(sc)

				self.update_component_row(row, amount, "deductions", adding=1, adding_if_not_exist=1)




		get_start_month_dates = frappe.db.sql(""" SELECT total_leave_days FROM `tabLeave Application`  WHERE employee='%s' 
			and leave_type='Leave Without Pay' and 
			from_date <= '%s' and to_date >= '%s' """%(self.employee , self.start_date,self.start_date))
		# frappe.throw(str(get_start_month_dates))
		# frappe.throw(str(get_start_month_dates ))
		self.payment_days = self.payment_days - self.absent_days


	def calculate_net_pay(self):

		self.gross_pay = 0
		self.total_deduction = 0
		self.net_pay = 0
		for i in self.earnings :
			# msgprint(str(i.amount))
			try :
				self.gross_pay += float(i.amount) 
			except:
				pass
		for i in self.deductions:
			try :
				self.total_deduction+= float(i.amount)
			except:
				pass

		self.net_pay = self.gross_pay - self.total_deduction - (self.total_loan_repayment or 0)
		self.rounded_total = rounded(self.net_pay) or 0
	def set_loan_repayment(self):
		self.set('loans', [])
		self.total_loan_repayment = 0
		self.total_interest_amount = 0
		self.total_principal_amount = 0

		for loan in self.get_loan_details():
			self.append('loans', {
				'loan': loan.name,
				'total_payment': loan.total_payment,
				'interest_amount': loan.interest_amount,
				'principal_amount': loan.principal_amount,
				'loan_account': loan.loan_account,
				'interest_income_account': loan.interest_income_account
			})

			self.total_loan_repayment += loan.total_payment
			self.total_interest_amount += loan.interest_amount
			self.total_principal_amount += loan.principal_amount
	def get_loan_details(self):
		return frappe.db.sql("""select rps.principal_amount,
				rps.name as repayment_name, rps.interest_amount, l.name,
				rps.total_payment, l.loan_account, l.interest_income_account
			from
				`tabRepayment Schedule` as rps, `tabLoan` as l
			where
				l.name = rps.parent and rps.payment_date between %s and %s and
				l.repay_from_salary = 1 and l.docstatus = 1 and l.applicant = %s""",
			(self.start_date, self.end_date, self.employee), as_dict=True) or []

# MonthlySalarySlip.validate = PayrollEntry.validate