# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import datetime 

from dateutil.relativedelta import relativedelta

import frappe
from frappe.model.document import Document

class EmployeeContract(Document):

	def validate(self):
		if frappe.db.exists("Employee", self.employee):
			if self.department:
				frappe.db.sql("update tabEmployee set department='{}' where name='{}'".format(self.department,self.employee))
			if self.department:
				frappe.db.sql("update tabEmployee set branch='{}' where name='{}'".format(self.branch,self.employee))
			if self.national_id:
				frappe.db.sql("update tabEmployee set national_id='{}' where name='{}'".format(self.national_id,self.employee))
			if self.designation:
				frappe.db.sql("update tabEmployee set designation='{}' where name='{}'".format(self.designation, self.employee))








@frappe.whitelist()
def sumdates(start , dura , *args , **kwargs):
	start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
	# six_months = start_date.date() + relativedelta(months=+6)
	end_date = start_date.date() +  relativedelta(days=-1)+ relativedelta(months=+int(dura))

	return(end_date)



