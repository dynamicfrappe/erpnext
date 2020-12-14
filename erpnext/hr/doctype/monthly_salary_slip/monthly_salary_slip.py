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
		self.total_working_days = self.get_monthly_working_days_from_attendence_rule()
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
		self.status = self.get_status()
		self.validate_dates()
		self.check_existing()
		# self.check_sal_struct(self.end_date)
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
		return get_data[0][0]
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
		for i in salary_component.earnings  :
					self.set_component(i , 'earnings')
		for i in salary_component.deductions :
					self.set_component(i , 'deductions')


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
		self.set(typ,[])
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
				self.calculate_attendance()
				self.calculate_Tax()
				self.calculate_net_pay()


	def check_sal_struct(self, starting_date):


		salary_structure = frappe.db.sql(""" SELECT name FROM `tabMulti salary structure` WHERE  from_date  <=  '%s' 
		 and status='open' """%starting_date)
		if not salary_structure :
			frappe.msgprint(_("No active or default Salary Structure found for employee {0} for the given dates")
				.format(self.employee), title=_('Salary Structure Missing'))
		else:

			pass


