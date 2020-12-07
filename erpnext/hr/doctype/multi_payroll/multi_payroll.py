# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MultiPayroll(Document):
	def fill_employee_details(self):
		self.set('employees', [])
		employees = [self.get_emp_list()]
		if not employees:
			frappe.throw(_("No employees for the mentioned criteria"))
		# frappe.throw((str(employees)))
		for d in employees:
			row  = self.append('employees', {})
			row.employee = d
		self.number_of_employees = len(employees)
		# if self.validate_attendance:
		# 	return self.validate_employee_attendance()


	def get_emp_list(self):
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""
		# cond = self.get_filter_condition()
		# cond += self.get_joining_relieving_condition()

		# condition = ''
		# if self.payroll_frequency:
		# 	condition = """and payroll_frequency = '%(payroll_frequency)s'"""% {"payroll_frequency": self.payroll_frequency}

		# sal_struct = frappe.db.sql_list("""
		# 		select
		# 			name from `tabSalary Structure`
		# 		where
		# 			docstatus = 1 and
		# 			is_active = 'Yes'
		# 			and company = %(company)s and
		# 			ifnull(salary_slip_based_on_timesheet,0) = %(salary_slip_based_on_timesheet)s
		# 			{condition}""".format(condition=condition),
		# 		{"company": self.company, "salary_slip_based_on_timesheet":self.salary_slip_based_on_timesheet})
		# if sal_struct:
		# 	cond += "and t2.salary_structure IN %(sal_struct)s "
		# 	cond += "and %(from_date)s >= t2.from_date"
		# 	emp_list = frappe.db.sql("""
		# 		select
		# 			distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
		# 		from
		# 			`tabEmployee` t1, `tabMulti salary structure` t2
		# 		where
		# 			t1.name = t2.employee
		# 			and t2.docstatus = 1
		# 	%s order by t2.from_date desc
		# 	""" % cond, {"sal_struct": tuple(sal_struct), "from_date": self.end_date}, as_dict=True)
		# department_con = """ and  t1.department = '%s'  """%self.department
		assignment = """SELECT  distinct t1.employee , t2.salary_structure 
		 FROM `tabMulti salary structure` AS t1  Inner join  `tabSalary structure Template` AS t2
		 ON t1.name = t2.parent  
		 WHERE type = '%s' 
		 and t2.docstatus = 1"""%self.payroll_type 
		if self.department : 
		 	department_con = """ and  t1.department = '%s'  """%self.department
		 	assignment += department_con
		employees = frappe.db.sql(assignment)
		try :
			data = employees[0][0]
		except:
			data = None
		return  data


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
