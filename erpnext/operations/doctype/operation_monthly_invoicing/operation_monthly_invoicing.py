# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import collections
from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

class OperationMonthlyInvoicing(Document):
	def validate (self):
		employee_list = [x.employee for x in self.monthly_details_data] 
		duplicated_employees = [item for item, count in collections.Counter(employee_list).items() if count > 1]
		if len(duplicated_employees) :
			message = '<br/> <ol>' + " ".join([str('<li>' + str(item) + '</li>') for item in duplicated_employees])
			frappe.throw(_("Employees is duplicated {} ".format(message)))


	def before_save(self):
		self.transaction_no = self.name
		self.total = 0
		count = 0
		for d in self.monthly_details_data:
			d.gross_salary = d.gross_salary  or 0
			d.social_insurance = d.social_insurance   or 0
			d.laptop = d.laptop or 0
			d.ohs_courses = d.ohs_courses or 0
			d.medical_insurance = d.medical_insurance   or 0
			d.mobile_package = d.mobile_package   or 0
			d.ohs_tools = d.ohs_tools  or 0
			d.total = d.gross_salary + d.social_insurance + d.laptop + d.ohs_courses + d.medical_insurance + d.mobile_package + d.ohs_tools
			self.total +=  d.total
			if d.sales_invoice :
				count = 1

		if count == 0 :
			self.status = 'Active'
		elif count < len (self.monthly_details_data):
			self.status = 'partially Invoiced'
		elif count == len(self.monthly_details_data):
			self.status = "Invoiced"

	def create_invoice (self,selected_rows):
		
		
		self.save()
		selected_rows = [frappe._dict(i) for i in selected_rows]
		
		names = [x.name for x in selected_rows]
		invoiced_items = [s for s in self.monthly_details_data if not s.sales_invoice and s.name in names]
		names = ",".join([("'" + str(s.name) + "'") for s in invoiced_items ])
		income_account = self.income_account
		currency = frappe.get_cached_value('Company',  self.company,  "default_currency")
		if not income_account:
			frappe.throw(_("Please Set Income Account"))
		debit_to = self.debit_to
		if not debit_to:
			frappe.throw(_("Please Set Depit To Account"))
		if not invoiced_items:
			frappe.throw(_("All items are invoiced or nothing Select to Invoiced "))
		if self.invoicing_type == 'One Invoice':

				total = sum([int(s.total) for s in invoiced_items])
				if not total:
					frappe.throw(_("Cann't Create Invoice for 0 Total ")) 
				item_code = frappe.db.get_single_value("Operations Settings", "one_invoice_item_service")
				if not item_code:
					frappe.throw(_("Please Set One Invoice Item in Operations Settings"))
				si = frappe.new_doc("Sales Invoice")
				si.company = self.company
				si.currency = currency
				si.customer=self.customer
				si.naming_series = 'ACC-SINV-.YYYY.-'
				si.due_date = self.date
				si.posting_date = self.date
				tax = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=self.company)
				if tax :
					si.taxes_and_charges = str(tax['taxes_and_charges'])
					si.set_taxes()
				si.debit_to = debit_to
				si.append("items", {
					"item_code": item_code,
					"income_account": income_account,
					"qty": 1,
					"rate" : total,
					"amount":total
				})

				# si.set_missing_values()
				si.save()
				frappe.db.sql (""" update `tabMonthly Details` set sales_invoice = '{sales_invoice}' where name in ({names})  """.format(sales_invoice=si.name , names = names))
				frappe.db.commit()
				frappe.msgprint(_("Sales Invoice {0} Was Created").format("<a href='#Form/Sales Invoice/{0}'>{0}</a>".format(si.name)))

		elif self.invoicing_type == 'Detailed Invoicing':
			for i in invoiced_items:
				if not i.total:
					frappe.msgprint(_("Cann't Create Invoice for 0 Total ") ,title = _("Error in Employee {}".format(i.employee)),indicator='red')
					continue 
				item_code = frappe.db.sql("select item_code from tabItem where item_code like '%{employee_name}%' order by name desc limit 1".format(employee_name = i.employee_name))
				if not item_code:

					frappe.msgprint("select item_code from tabItem where item_code like '%{employee_name}%' order by name desc limit 1".format(employee_name = i.employee_name))
					frappe.msgprint(_("Please Create Item for Employee {}".format(i.employee)),title = _("Error in Employee {}".format(i.employee)),indicator='red')
					continue
				item_code = item_code[0][0]
				si = frappe.new_doc("Sales Invoice")
				si.company = self.company
				si.currency = currency
				si.naming_series = 'ACC-SINV-.YYYY.-'
				si.customer=self.customer
				si.due_date = self.date
				si.posting_date = self.date
				si.debit_to = debit_to
				tax = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=self.company)
				if tax :
					si.taxes_and_charges = str(tax['taxes_and_charges'])
					si.set_taxes()
				si.append("items", {
					"item_code": item_code,
					"income_account": income_account,
					"qty": 1,
					"rate" : i.total,
					"amount":i.total
				})
				si.set_missing_values()
				si.save()
				i.sales_invoice = si.name
				frappe.msgprint(_("Sales Invoice {0} Was Created for Employee {1}").format("<a href='#Form/Sales Invoice/{0}'>{0}</a>".format(si.name),i.employee))
				frappe.db.sql (""" update `tabMonthly Details` set sales_invoice = '{sales_invoice}' where name = '{name}'  """.format(sales_invoice=si.name , name = i.name))
				frappe.db.commit()
		self.monthly_details_data = frappe.get_doc("Operation Monthly Invoicing",self.name).monthly_details_data
		
		self.save()


    






