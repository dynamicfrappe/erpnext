# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	try:
		add_salary_component()
		print("add_salary_component\n Done ")
	except Exception as e:
		print( 'add_salary_component\n' + str(e) )
	try:
		add_attendance_rule()
		print ("add_attendance_rule\n Done ")
	except Exception as e:
		print('add_attendance_rule\n' + str(e))




def add_salary_component():
	earnings = ["Overtime" , "Weekend Overtime" , "Holiday Overtime" , "Staying Up Late"]
	deductions = ["Less Time","Delays" , "Delays Penality" , "Absnet" , "Absent Penality" , "Loan" , "Advance" , "Medical Insurance" , "Social Insurance" , "Fingerprint Forgetten Penality"]
	for i in earnings:
		if  not frappe.db.exists('Salary Component', str(i)):
				abbr = ''.join([ s[0].upper()+s[-1].lower() + '_' for s in i.split() ])+"E"
				frappe.db.sql(""" insert into `tabSalary Component` (name,salary_component , type , salary_component_abbr ) 
				values ('{name}' , '{name}' , 'Earning' , '{abbr}' )
				""".format(name = i , abbr = abbr))
	for i in deductions:
		if  not frappe.db.exists('Salary Component', str(i)):
				abbr = ''.join([ s[0].upper()+s[-1].lower() + '_' for s in i.split() ])+"D"
				frappe.db.sql(""" insert into `tabSalary Component` (name,salary_component , type , salary_component_abbr ) 
				values ('{name}' , '{name}' , 'Deduction' , '{abbr}' )
				""".format(name = i , abbr = abbr))


def add_attendance_rule():
	name = "Default"
	if  not frappe.db.exists('Attendance Rule', str(name)):
		doc = frappe.new_doc('Attendance Rule')
		doc.role_name = name
		doc.type = "Daily"
		doc.working_type = "Shift"
		doc.fingerprint_forgetten_penlaity_salary_component = "Fingerprint Forgetten Penality"
		doc.salary_componat_for_late = "Delays"
		doc.salary_component_for_late_penalty = "Delays Penality"
		doc.absent__component = "Absnet"
		doc.abset_penalty_component = "Absent Penality"
		doc.overtime_salary_component = "Overtime"
		doc.staying_up_late_salary_component = "Staying Up Late"
		doc.less_time_salary_component = "Less Time"
		doc.overtime_in_weekend_salary_component = "Weekend Overtime"
		doc.overtime_in_holiday_salary_component = "Holiday Overtime"
		doc.overtime_factor_in_weekend = 2
		doc. evening_overtime_factor = 1.65
		doc.overtime_factor_in_holidays = 2
		doc.save()

