# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Taxperiod(Document):

	def getTaxType(self):
		typeList=[]
		if self.taxperioddetails:
			for d in self.taxperioddetails:
				typeList.append(d.taxclass)
			typeList.append("All")
			return typeList
		return typeList

	def createAddTax(self,type):
		if type=="All":
			type=""
		self.save()
		doc = frappe.new_doc("Value Added Tax")
		doc.fromdae=self.fromdae
		doc.todate=self.todate
		doc.taxtype=type
		doc.refdoc="Tax period"
		doc.docname=self.name

		doc.save()
		if type != "All":
			frappe.db.sql("update `tabTax Period Details` set refdoc='{}' where taxclass='{}' and parent='{}'".format(doc.name,type,self.name))
		else:
			frappe.db.sql("update `tabTax Period Details` set refdoc='{}' where  and parent='{}'".format(doc.name,self.name))

		return doc.name


