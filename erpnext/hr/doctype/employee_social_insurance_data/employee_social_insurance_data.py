# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmployeeSocialInsuranceData(Document):
	def getInsuranceSetting(self):
		min_insurance_salary=frappe.db.get_single_value("Social Insurance Settings","min_limit")
		max_insurance_salary=frappe.db.get_single_value("Social Insurance Settings","max_limit")
		data={"min":min_insurance_salary,"max":max_insurance_salary}
		return data
		
	def getbasicSalarySetting(self):
		min_basic_salary=frappe.db.get_single_value("Social Insurance Settings","bs_minimum")
		max_basic_salary=frappe.db.get_single_value("Social Insurance Settings","bs_maximum")
		data={"min":min_basic_salary,"max":max_basic_salary}
		return data











	



