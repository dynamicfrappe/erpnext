# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AssetsReturn(Document):
	pass

@frappe.whitelist() 
def create_asset_movement(name,*args,**kwargs):
	frm = frappe.get_doc("Assets Return" , name)
	doc=frappe.new_doc("Asset Movement")
	doc.company=frm.company
	doc.purpose="Receipt"
	
	for a in frm.custody_request_item:
		row=doc.append("assets", {})
		row.asset=a.asset
		row.target_location=frappe.db.get_value("Company",frm.company,"default_asset_location")
		if(frm.reference_document_type=="Employee"):
			row.from_employee=frappe.db.get_value(frm.reference_document_type,frm.reference_document_name,"first_name")
		else:
			try:
				row.source_location=frappe.db.get_value(frm.reference_document_type,frm.reference_document_name,"location")
			except:
				print("error")
			
        #row.target_location=frappe.db.get_value("Company", "SKY", "default_asset_location")
	doc.reference_doctype = "Assets Return"
	doc.reference_name = name
	#doc.save()
	return doc








    



	

