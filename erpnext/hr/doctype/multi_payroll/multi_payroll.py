# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import  datetime


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
		

	def get_emp_list(self):
		assignment = """SELECT  distinct t1.employee , t2.salary_structure  , em.date_of_joining , em.relieving_date
		 FROM `tabMulti salary structure` AS t1   join  `tabSalary structure Template` AS t2
		 ON t1.name = t2.parent 
		 join `tabEmployee` AS em on   t1.employee_name = em.employee_name
		 WHERE type = '%s' 
		 and t2.docstatus = 1 and t1.status='open' """%self.payroll_type 
		if self.department : 
		 	department_con = """ and  t1.department = '%s'  """%self.department
		 	assignment += department_con
		self.employee_data = frappe.db.sql(assignment)
		try :
			data =[ i for i in self.employee_data ]
		except:
			data = None
		return  data
	def set_component(self,salary_slip,i,typ):	
			row = salary_slip.append(typ, {})
			row.salary_component = i.salary_component
			row.abbr= i.abbr
			row.statistical_component = i.statistical_component
			row.deduct_full_tax_on_selected_payroll_date = i.deduct_full_tax_on_selected_payroll_date
			row.depends_on_payment_days =i.depends_on_payment_days
			row.is_tax_applicable = i.is_tax_applicable
			row.exempted_from_income_tax = i.exempted_from_income_tax
			row.formula = i.formula
			row.amount = i.amount
			salary_slip.save()
	def create_salary_slips(self ):
		if self.employees:
			for salary_structure in self.employees :
				salary_slip = frappe.new_doc('Monthly Salary Slip')
				salary_slip.posting_date = datetime.today()
				salary_slip.employee = salary_structure.employee
				employe = frappe.get_doc("Employee" ,salary_structure.employee )
				salary_slip.payroll_type = self.payroll_type
				if employe.date_of_joining <= datetime.strptime( self.start_date, "%Y-%m-%d").date():
					salary_slip.start_date = self.start_date
				else:
					salary_slip.start_date=employe.date_of_joining

				if employe.relieving_date >= datetime.strptime( self.end_date, "%Y-%m-%d").date():
					salary_slip.end_date = self.end_date
				else:
					salary_slip.start_date=employe.relieving_date

				



				salary_slip.total_working_days =  frappe.db.get_value("Company" , 
										          frappe.db.get_single_value("Global Defaults" ,"default_company"),
										          'default_monthly_work_days')
				try :
					a = 0 
				except:
					pass
				salary_slip.payment_days = 30
				salary_slip.salary_structure = salary_structure.salary_structure
				salary_slip.save()
				structure = frappe.get_doc("Salary Structure" , salary_structure.salary_structure ) 
				#add Errnings
				for i in structure.earnings :
					self.set_component(salary_slip , i , 'earnings')
				#add Errnings
				for i in structure.deductions :
					self.set_component(salary_slip , i , 'deductions')





	def get_filter_condition(self):
		
		cond = ''
		for f in ['company', 'branch', 'department', 'designation']:
			if self.get(f):
				cond += " and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		return cond
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
				"doctype": "Salary Slip",
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