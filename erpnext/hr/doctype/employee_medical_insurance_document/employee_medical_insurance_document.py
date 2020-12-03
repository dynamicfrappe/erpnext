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


@frappe.whitelist()
def get_employee(*args,**kwargs):

	employees = frappe.db.sql(""" SELECT name FROM `tabEmployee` WHERE status="Active"  AND document IS NULL   """)
	return(employees)