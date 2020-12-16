# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmployeeMedicalInsuranceDocument(Document):




	def on_submit(self):
		a= frappe.db.sql(""" UPDATE `tabEmployee` SET document = '%s' , medication_card_recieving_date ='%s',employee_share_ratio ='%s'
		 WHERE name='%s' """%(self.insurance_document ,self.insurance_card_start_date , self.employee_fee ,self.employee ))
	def set_family_members(self):
		self.set("employee_medical_insurance_members", [])
		employee_family_data = frappe.db.sql(""" SELECT relation ,name1 , age FROM 
		`tabEmployee Family Details` WHERE parent='%s' """%self.employee)
		for i in range(0,int(self.family_member_count)) :
			row = self.append('employee_medical_insurance_members', {})
			try :
				row.relation = employee_family_data[i][0]
				row.member = employee_family_data[i][1]
				row.age = employee_family_data[i][2]
				if self.insurance_document: 
					row.document_no =self.insurance_document
			except:
				pass



@frappe.whitelist()
def get_employee(*args,**kwargs):

	employees = frappe.db.sql(""" SELECT name FROM `tabEmployee` WHERE status="Active"  AND document IS NULL   """)
	return(employees)


@frappe.whitelist()
def get_employee_family_members(*args,**kwargs):
	if args[5].get('employee') :
		 members = frappe.db.sql (""" SELECT relation FROM `tabEmployee Family Details` WHERE parent='%s'"""%args[5].get('employee'))
		 return ([i for i in members])