# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class EmployeePenality(Document):
	def on_submit(self):
		rule = frappe.get_doc("Penality Type", self.penality_type)
		violation = frappe.get_doc("Violations", self.penality)
		if rule :
			if rule.code == str(1):

					if self.penality_factor:
						doc = frappe.new_doc("Additional Salary")
						doc.count = self.penality_factor
						doc.salary_component = violation.salary_component
						doc.employee = self.employee
						doc.overwrite_salary_structure_amount = 1
						doc.amount_based_on_formula = 1
						doc.type = "Deduction"
						doc.payroll_date = self.payroll_effect_date
						doc.description = self.penality + "\n" + str(self.notes)
						doc.insert()
						doc.submit()
			if rule.code == str(2):
						doc = frappe.new_doc("Warnings")
						doc.employee = self.employee
						doc.date = self.posting_date
						doc.violation = self.penality
						doc.type = 2
						doc.insert()
						doc.submit()
			if rule.code == str(3):
						doc = frappe.new_doc("Warnings")
						doc.employee = self.employee
						doc.date = self.posting_date
						doc.violation = self.penality
						doc.type = 1
						doc.insert()
						doc.submit()



	def get_pervious_Penalities(self):
		self.pervious_penalities = '0'
		if self.employee and self.penality:
			sql = """
			select count(*) as pervious_count from `tabEmployee Penality` where employee = '{employee}' and penality = '{penality}' and docstatus=1 
			and TIMESTAMPDIFF(MONTH, posting_date, current_date()) < 6
			""".format(employee = self.employee , penality= self.penality )
			# frappe.msgprint(str(sql))
			count = frappe.db.sql(sql,as_dict=1)
			# frappe.msgprint(str(count))
			if count:
				self.pervious_penalities= str(count [0].pervious_count)
		self.get_Rule()
	def get_Rule(self):
		self.article_number = "#"
		if self.penality :
			violation = frappe.get_doc("Violations", self.penality)
			if violation :
				self.article_number = str(violation.article_number)
				type = None
				factor = 0
				for i in violation.penality_rules:
					if i.index <= int(self.pervious_penalities) + 1:

						type = i.penality_type
						factor = i.factor or 0
				if type :
					rule = frappe.get_doc("Penality Type" , type)
					self.penality_type = str(rule.name)
					self.penality_description =str(rule.description)
					self.penality_factor = factor or 0

				else :
					self.penality_type = ""
					self.penality_description = ""
					self.penality_factor = 0
