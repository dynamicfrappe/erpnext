# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now, date_diff , nowdate , nowtime
from dateutil.relativedelta import relativedelta

from frappe.model.document import Document

class OperationsInvoiceDues(Document):
	def delete(self):
		frappe.throw(_("Cann't Delete Operations Invoice Dues"))
	def set_totals (self):
		self.total_invoiced = 0
		self.total_remaining = 0
		self.total_active = 0
		self.total_hold = 0
		self.total_resources = 0
		self.total_tools = 0
		self.total_qty = 0
		self.total_resources_fee = 0
		self.total_tools_fee = 0
		self.total_fee = 0
		for i in getattr(self,'items',[]):

			if getattr(i,'resource',None):
				self.total_resources += i.qty
				self.total_resources_fee +=i.total if i.status == 'Active'  else 0

			if getattr(i,'tool',None):
				self.total_tools += i.qty
				self.total_tools_fee +=i.total if i.status == 'Active'  else 0

			if i.status == 'Active':
				self.total_active +=i.qty
			else :
				self.total_hold += i.qty

			if i.invoiced:
				self.total_invoiced +=i.qty
			else :
				self.total_remaining += i.qty
		self.total_fee = self.total_tools_fee + self.total_resources_fee
		self.total_qty = self.total_tools + self.total_resources
	def create_invoice(self):
		if not self.invoiced :
			invoice = frappe.new_doc("Operation Sales Invoice")
			invoice.customer = self.customer
			# invoice.company =  self.company
			invoice.invoice_due = self.name
			invoice.customer_agreement = self.agreement
			invoice.posting_date = nowdate()
			invoice.payment_date = self.date
			invoice.posting_time = nowtime()
			invoice.project = self.project
			invoice.cost_center = self.cost_center
			invoice.total_qty = 0
			invoice.total = 0
			invoice.base_grand_total = 0
			invoice.grand_total = 0
			invoice.status = 'Draft'

			for item in getattr(self, 'items', []):
				if item.status == 'Active' and not item.invoiced :
					# untransferred_qty = item.qty - item.transferred_qty
					# if untransferred_qty > 0 :
					invoice_child = invoice.append('items')
					invoice_child.item = item.item_code
					invoice_child.item_name = item.item_name
					invoice_child.price = item.rate
					invoice_child.qty = item.qty
					invoice_child.total = item.total
					invoice_child.customer_agreement = self.agreement
					invoice_child.invoice_due = self.name
					invoice_child.customer_tool = item.tool
					invoice_child.customer_resource = item.resource
					invoice.total_qty += item.qty
					invoice.total += item.total
					item.invoiced = 1


			invoice.base_grand_total = invoice.total
			invoice.grand_total = invoice.total
			invoice.rounded_total = round(invoice.grand_total, 0)
			invoice.base_rounded_total = round(invoice.grand_total, 0)

			if not getattr(invoice, 'items', None):
				frappe.msgprint(_('There is no Items To Transfer'),indicator='red')
			else :
				invoice.insert()
				self.invoiced = all([i.invoiced for i in self.items])
				self.save()