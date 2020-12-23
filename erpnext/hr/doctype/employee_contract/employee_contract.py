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
		is_ended = datetime.datetime.strptime(str(self.contract_end_date), '%Y-%m-%d').date() < datetime.datetime.strptime(str(utils.today()), '%Y-%m-%d').date()
		if is_ended :
				self.status = "Ended"

	def validate_employee_active_cotracts(self):
		# frappe.throw( str(utils.today()))
		end_date= False
		if frappe.db.exists("Employee", self.employee):

			employee_active_contract = frappe.db.sql("""SELECT contract_end_date FROM `tabEmployee Contract` WHERE 
				 employee ='%s' and status='Active'"""%self.employee)
			if employee_active_contract:
				end_date =employee_active_contract[0][0]
		if end_date:
			valid_start_date = datetime.datetime.strptime(self.contract_start_date, '%Y-%m-%d').date() > end_date
			if not valid_start_date:
				return end_date+relativedelta(days=+1)
		return False

	def RenewContract(self):
		end_date=datetime.datetime.strptime(self.contract_end_date, '%Y-%m-%d').date()
		doc = frappe.new_doc("Employee Contract")
		doc.employee=self.employee
		doc.employee_name=self.employee_name
		doc.national_id=self.national_id
		doc.employee_addresse=self.employee_addresse
		doc.employee_joined_day=self.employee_joined_day
		doc.compnay=self.compnay
		doc.contract_type=self.contract_type
		doc.company_representative_name=self.company_representative_name
		doc.status="Active"
		doc.company_representative_jop_title=self.company_representative_jop_title
		doc.company_addresse=self.company_addresse
		doc.contract_duration=self.contract_duration
		doc.contract_start_date=end_date+relativedelta(days=+1)
		doc.contract_end_date=end_date+relativedelta(months=+int(self.contract_duration))
		doc.department=self.department
		doc.branch=self.branch
		doc.designation=self.designation
		doc.comprehensive_salary=self.comprehensive_salary
		doc.insurance_salary=self.insurance_salary
		doc.net_salary=self.net_salary
		doc.contract_template=self.contract_template
		doc.attached_image=self.attached_image
		doc.save()
		#frappe.set_route("Form", "Employee Contract", doc.name);
		#frappe.set_route("List", "Employee Contract");
		frappe.db.sql("update `tabEmployee Contract` set isrenewd=1 where name='{}'".format(self.name))
		frappe.msgprint("Contract Renewed")
		return "true"



@frappe.whitelist()
def sumdates(start , dura , *args , **kwargs):
	start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
	end_date = start_date.date() +  relativedelta(days=-1)+ relativedelta(months=+int(dura))

	return(end_date)



