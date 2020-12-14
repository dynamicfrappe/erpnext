# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class SalaryStructureType(Document):
	def validate(self):
		if self.is_main:
			frappe.db.sql("""
			update `tabSalary Structure Type`  set is_main = 0 where is_main = 1
			""")
		else:
			result = frappe.db.sql("""
			select * from `tabSalary Structure Type`   where is_main = 1
			""")
			if not result :
				self.is_main = 1

