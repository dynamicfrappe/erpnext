# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MultiPayroll(Document):
	def fill_employee_details(self):
		self.set('employees', [])
		employees = self.get_emp_list()
		if not employees:
			frappe.throw(_("No employees for the mentioned criteria"))
	
		for d in employees:
			valid = validate_salary_slip(d,self. start_date , self.end_date ,self.payroll_type)
			if valid:
				row  = self.append('employees', {})
				row.employee = d
		self.number_of_employees = len(self.employees)
		

	def get_emp_list(self):
		# data = []
		assignment = """SELECT  distinct t1.employee , t2.salary_structure 
		 FROM `tabMulti salary structure` AS t1   join  `tabSalary structure Template` AS t2
		 ON t1.name = t2.parent  
		 WHERE type = '%s' 
		 and t2.docstatus = 1"""%self.payroll_type 
		if self.department : 
		 	department_con = """ and  t1.department = '%s'  """%self.department
		 	assignment += department_con
		employees = frappe.db.sql(assignment)
		try :
			data =[ i[0] for i in employees ]
		except:
			data = None
		return  data

	# def create_salary_slips(self):
	# 	if self.employees:
	# 		for employee in self.employees:
	# 			valid = 

	# 	# self.check_permission('write')
		# self.created = 1
		# emp_list = [d.employee for d in self.get_emp_list()]
		# if emp_list:
		# 	args = frappe._dict({
		# 		"salary_slip_based_on_timesheet": self.salary_slip_based_on_timesheet,
		# 		"payroll_frequency": self.payroll_frequency,
		# 		"start_date": self.start_date,
		# 		"end_date": self.end_date,
		# 		"company": self.company,
		# 		"posting_date": self.posting_date,
		# 		"deduct_tax_for_unclaimed_employee_benefits": self.deduct_tax_for_unclaimed_employee_benefits,
		# 		"deduct_tax_for_unsubmitted_tax_exemption_proof": self.deduct_tax_for_unsubmitted_tax_exemption_proof,
		# 		"payroll_entry": self.name
		# 	})
		# 	if len(emp_list) > 30:
		# 		frappe.enqueue(create_salary_slips_for_employees, timeout=600, employees=emp_list, args=args)
		# 	else:
		# 		create_salary_slips_for_employees(emp_list, args, publish_progress=False)
		# 		# since this method is called via frm.call this doc needs to be updated manually
		# 		self.reload()

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