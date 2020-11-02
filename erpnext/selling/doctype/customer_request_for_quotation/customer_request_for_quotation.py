# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CustomerRequestforQuotation(Document):
	pass



@frappe.whitelist() 
def create_quotation(name  , *args,**kwargs):
	frm = frappe.get_doc("Customer Request for Quotation" , name)
	doc = frappe.new_doc('Quotation')
	doc.company = frm.company
	doc.customer_rfq = frm.name
	doc.quotation_to = "Customer"
	doc.party_name = frm.customer
	return doc
