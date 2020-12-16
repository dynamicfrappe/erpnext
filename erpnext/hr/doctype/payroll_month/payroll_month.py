# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import  datetime


from dateutil.relativedelta import relativedelta
class PayrollMonth(Document):
	def validate(self):
		if not self.month_for_year():
			frappe.throw("Month validation Error")
		if datetime.strptime(self.end_date, "%Y-%m-%d").date() != self.set_end_date():
			frappe.throw("Invalid End Date")
	def get_attendance_years(self):
		year = datetime.today().year
		year_list = range(2019 ,year+2 )

		return "\n".join(str(x) for x in year_list)
	def month_for_year(self):
		dublicated = frappe.db.sql("""SELECT name FROM `tabPayroll Month` WHERE month='%s' AND year='%s' and docstatus=1"""%(self.month ,self.year))
		if dublicated:
			return False
		else:
			return True
	def set_end_date(self):
		return  (datetime.strptime(self.start_date, "%Y-%m-%d").date() +  relativedelta(months=+1))+relativedelta(days=-1)

	def set_attendance_end_date(self):
		return  (datetime.strptime(self.attendance_start_date, "%Y-%m-%d").date() +  relativedelta(months=+1))+relativedelta(days=-1)

	def get_strcuture_type_option(self):
		a=  frappe.db.sql(""" SELECT type FROM `tabSalary Structure Type` """)
		return([i[0] for i in a])


@frappe.whitelist()
			
def make_payroll_entry(name ,type,frcv, department=None,*args,**kwargs):
	doc = frappe.new_doc('Multi Payroll')
	frm =  frappe.get_doc("Payroll Month" , name)
	doc.payroll_month = name
	doc.posting_date = datetime.today()
	doc.payroll_frequency = "Monthly"
	doc.payroll_type = frcv
	doc.start_date = frm.start_date
	doc.end_date = frm.end_date
	if department :
		doc.department = department
	doc.save()
	row = frm.append('payroll_records', {})
	row.payroll = doc.name
	row.type = frcv
	if department :
		row.department = department
	frm.save()
	return doc.name