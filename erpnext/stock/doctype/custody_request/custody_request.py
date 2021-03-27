# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _ 
class Custodyrequest(Document):






	# @frappe.whitelist() 
	def create_asset_movement(self):
		doc = frappe.new_doc('Asset Movement')
		doc.company = self.company
		# doc.purpose = ''
		if self.reference_document_type == "Employee" :
			doc.purpose = 'Issue'
		else :
			doc.purpose = 'Transfer'

		doc.save()
		frappe.db.commit()
		

		return doc

@frappe.whitelist() 
def create_asset_movement(name , *args,**kwargs):
		frm = frappe.get_doc("Custody request" , name)
		doc = frappe.new_doc('Asset Movement')
		doc.company = frappe.db.get_default("Company")
		doc.transaction_date = frm.required_date
		# doc.purpose = ''
		if frm.reference_document_type == "Department" :
			doc.purpose = 'Transfer'
		else :
			doc.purpose = 'Issue'

		doc.reference_doctype = "Custody request"
		doc.reference_name = name
		# for i in frm.get('custody_request_item'):
		# 	for x in range(0,i.qty):
		# 		row=doc.append('assets',{})
		# 		row.asset=i.item
		# 		if frm.reference_document_type == "Employee":
		# 			row.to_employee = frm.reference_document_name




		# doc.save()
		# frappe.db.commit()
		

		return (doc)


@frappe.whitelist() 
def get_asset_costudian(name , *args ,**kwargs):
	data = frappe.db.sql("""  SELECT asset_name ,value_after_depreciation FROM `tabAsset` WHERE custodian = '%s'""" %name)
	return data


@frappe.whitelist() 
def get_asset_department(name , *args ,**kwargs):
	data = frappe.db.sql("""  SELECT asset_name ,value_after_depreciation FROM `tabAsset` WHERE department = '%s'""" %name)
	return data



@frappe.whitelist() 
def get_asset_project(name , *args ,**kwargs):
	data = frappe.db.sql("""  SELECT asset_name ,value_after_depreciation FROM `tabAsset` WHERE project = '%s'""" %name)
	return data
