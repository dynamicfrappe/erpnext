# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Requestforexpenceclaim(Document):
	def validate(self):
		total=0
		for ex in self.expence:
			total +=int(ex.amount)
		self.total=total

	def getEmployee(self):
		emplist = []
		data = frappe.db.sql("""select employee from `tabEmployee Advance`""", as_dict=1)
		for emp in data:
			emplist.append(emp.employee)
		return emplist


