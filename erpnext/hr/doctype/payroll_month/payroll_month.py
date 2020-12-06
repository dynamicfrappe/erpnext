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
		year_list =[ x for x in range(2019 ,year+1 )]
		return "\n".join(str(x) for x in year_list)
	def month_for_year(self):
		dublicated = frappe.db.sql("""SELECT name FROM `tabPayroll Month` WHERE month='%s' AND year='%s' and docstatus=1"""%(self.month ,self.year))
		if dublicated:
			return False
		else:
			return True
	def set_end_date(self):
		return  (datetime.strptime(self.start_date, "%Y-%m-%d").date() +  relativedelta(days=-1)+ relativedelta(months=+1))