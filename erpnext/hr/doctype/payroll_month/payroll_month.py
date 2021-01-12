# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import  datetime ,timedelta
import calendar


from dateutil.relativedelta import relativedelta
class PayrollMonth(Document):
	def cancel(self):
		frappe.throw(_("Payroll Month is n't be able to cancel"))
	def submit(self):
		last_doc = frappe.db.sql("""
				 select * from `tabPayroll Month`  where company = '{company}' and docstatus = 1 and ifnull(is_closed,0) = 0  order by start_date desc LIMIT 1
							""".format(company=self.company), as_dict=1)
		if last_doc :
			last_doc = last_doc [0]
			frappe.throw(_("Please Close the opened Month {} first").format(last_doc.name))
		self.is_closed = 0
		self.status = 'Opened'
		self.save()
	def close_month(self):
		salary_slip_list = frappe.db.sql("""select * from `tabMonthly Salary Slip` where  month = '{name}' and docstatus = 1""".format(name=self.name))
		if not salary_slip_list :
			frappe.throw(_('There is  No Submitted Salary Slip in this Month'))
		frappe.db.sql("""update `tabPayroll Month` set is_closed = 1 , status = 'Closed' where name = '{name}' """.format(name=self.name))
		self.is_closed = 1
		self.status = 'Closed'
		frappe.msgprint(_("Done") ,title=_("Success"), indicator="green")
	def validate(self):
		if not self.month_for_year():
			frappe.throw("Month validation Error")
		if datetime.strptime(self.end_date, "%Y-%m-%d").date() != self.set_end_date():
			frappe.throw("Invalid End Date")
	def get_attendance_years(self):
		year = datetime.today().year
		year_list = [ i for i in range(2019 ,year+5 )]
		year_list.reverse()
		return "\n".join(str(x) for x in year_list)
	def month_for_year(self):
		dublicated = frappe.db.sql("""SELECT name FROM `tabPayroll Month` WHERE month='%s' AND year='%s' and company = '%s' and name <> '%s' """%(self.month ,self.year,self.company,self.name))
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
	def set_start_date (self):
		if not self.year:
			return
		start_date = None
		attendance_start_date = None
		last_doc = frappe.db.sql("""
		 select * from `tabPayroll Month`  where company = '{company}' and name <> '{name}'  order by start_date desc LIMIT 1
					""".format(company=self.company , name = self.name),as_dict=1)

		if not last_doc :

			start_day = frappe.db.get_single_value("HR Settings","payroll_month_start_day") or 0
			if not start_day:
				frappe.throw(_("Please Set Payroll Month Start Day in HR Settings"))
			attendance_start_day = frappe.db.get_single_value("HR Settings","attendance_month_start_day") or start_day
			month = datetime.strptime(str(self.month),  "%B").month

			self.start_date = datetime(int(self.year), month, start_day).date()
			self.attendance_start_date = datetime(int(self.year), month, attendance_start_day).date()
			self.end_date = datetime.strptime(str(self.start_date), "%Y-%m-%d").date() + relativedelta(
				months=+1) + relativedelta(days=-1)
			self.attendance_end_date = datetime.strptime(str(self.attendance_start_date),
														 "%Y-%m-%d").date() + relativedelta(months=+1) + relativedelta(
				days=-1)

		else:
			last_doc = last_doc[0]
			self.start_date = datetime.strptime(str(last_doc.start_date), "%Y-%m-%d").date() +  relativedelta(months=+1)
			self.attendance_start_date = datetime.strptime(str(last_doc.attendance_start_date), "%Y-%m-%d").date() +  relativedelta(months=+1)

			self.end_date = datetime.strptime(str(self.start_date), "%Y-%m-%d").date() + relativedelta(months=+1) + relativedelta(days=-1)
			self.attendance_end_date = datetime.strptime(str(self.attendance_start_date),"%Y-%m-%d").date() + relativedelta(months=+1) + relativedelta(days=-1)
			self.month = self.end_date.strftime("%B")
			self.year = str(self.end_date.strftime("%Y"))


@frappe.whitelist()
			
def make_payroll_entry(name ,type,frcv, department=None,*args,**kwargs):
	doc = frappe.new_doc('Multi Payroll')
	frm =  frappe.get_doc("Payroll Month" , name)
	doc.payroll_month = name
	doc.posting_date = datetime.today()
	doc.payroll_frequency = "Monthly"
	doc.payroll_type = frcv
	doc.start_date = frm.start_date
	doc.company = frm.company
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