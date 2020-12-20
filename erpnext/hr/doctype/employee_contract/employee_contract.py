# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe import utils
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
	
		if self.testing_duration and self.testing_start_date and self.testing_end_date :
			in_testing =  datetime.datetime.strptime(self.testing_end_date, '%Y-%m-%d').date() > datetime.datetime.strptime(utils.today(), '%Y-%m-%d').date()
			if in_testing :
				self.status = "On testing period"
			else:
				self.status = "Active"

		if self.testing_duration == 0 :
			self.status = "Active"

		self.check_ended_contract()

	def check_ended_contract(self):
		is_ended = datetime.datetime.strptime(self.contract_end_date, '%Y-%m-%d').date() > datetime.datetime.strptime(utils.today(), '%Y-%m-%d').date()
		if is_ended :
				self.status = "Ended"

	def validate_employee_active_cotracts(self):
		# frappe.throw( str(utils.today()))
		end_date= False
		if frappe.db.exists("Employee", self.employee):

			employee_active_contract = frappe.db.sql("""SELECT contract_end_date FROM `tabEmployee Contract` WHERE 
				 employee ='%s'"""%self.employee)
			if employee_active_contract:
				end_date =employee_active_contract[0][0]
		if end_date:
			valid_start_date = datetime.datetime.strptime(self.contract_start_date, '%Y-%m-%d').date() > end_date
			if not valid_start_date:
				return end_date+relativedelta(days=+1)
		return False


@frappe.whitelist()
def sumdates(start , dura , *args , **kwargs):
	start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
	end_date = start_date.date() +  relativedelta(days=-1)+ relativedelta(months=+int(dura))

	return(end_date)



