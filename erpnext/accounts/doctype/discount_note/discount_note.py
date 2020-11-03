# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


import random
import string
class DiscountNote(Document):
	def validate(self):
		# create_gl_entry(self.name)
		pass
	def on_submit(self):
		create_gl_entry(self.name)


@frappe.whitelist()
def create_gl_entry(name,*args ,**kwargs):

	cr_frm = frappe.get_doc("Discount Note" , name)
	company = frappe.get_doc("Company" ,cr_frm.company )
	df_cureency = company.default_currency
	new_doc = frappe.new_doc("GL Entry" )
	new_doc.posting_date = cr_frm.posting_date
	new_doc.transaction_date = cr_frm.posting_date
	new_doc.account = cr_frm.from_account
	new_doc.credit = cr_frm.discount_amoint
	new_doc.account_currency = df_cureency
	new_doc.docstatus =1
	new_doc.credit_in_account_currency = cr_frm.discount_amoint
	if cr_frm.type == 'Purchase Invoice' :
		party_type = "Supplier"
		party = cr_frm.supplier
	else :
		party_type = "Customer"
		party = cr_frm.customer
		new_doc.party_type = party_type
		new_doc.party = party

	new_doc.cost_center = cr_frm.cost_center
	new_doc.against = party
	new_doc.voucher_type = cr_frm.type
	new_doc.voucher_no = cr_frm.document_type
	new_doc.fiscal_year = '2020'
	new_doc.company = cr_frm.company
	new_doc.to_rename  =1
	new_doc.save(ignore_permissions = True)
	

	new_doc2 = frappe.new_doc("GL Entry" )
	new_doc2.posting_date = cr_frm.posting_date
	new_doc2.transaction_date = cr_frm.posting_date
	new_doc2.account = cr_frm.to_account
	new_doc2.debit = cr_frm.discount_amoint
	new_doc2.account_currency = df_cureency
	new_doc2.docstatus =1
	new_doc2.debit_in_account_currency = cr_frm.discount_amoint
	

	if cr_frm.type == 'Purchase Invoice' :
		new_doc2.party_type = party_type
		new_doc2.party = party
	new_doc2.cost_center = cr_frm.cost_center
	new_doc2.against = party
	new_doc2.voucher_type = cr_frm.type
	new_doc2.voucher_no = cr_frm.document_type
	new_doc2.fiscal_year = '2020'
	new_doc2.company = cr_frm.company
	new_doc2.to_rename  =1
	new_doc2.save(ignore_permissions = True)

	name = create_name()
	invoice = frappe.db.sql("""INSERT INTO `tabPurchase invoice Discount` (name ,parent ,name1 ,account ,value ,parentfield,parenttype )
							 VALUES ('%s','%s','%s' , '%s' , '%s','%s','%s')"""%(str(name),str(cr_frm.document_type) , str(cr_frm.name),
							 										str(cr_frm.to_account),cr_frm.discount_amoint ,'discount_note_table',str(cr_frm.type)) )
	amount =float(cr_frm.unallocated_amount - float(cr_frm.discount_amoint))
	total_note = frappe.db.sql(""" SELECT SUM(value) FROM `tabPurchase invoice Discount` WHERE parent='%s' """%cr_frm.document_type )
	if cr_frm.type == 'Purchase Invoice' :
		
		frappe.db.sql(""" UPDATE `tabPurchase Invoice` SET outstanding_amount = %d  ,
							total_discount_note =%d WHERE name ='%s'"""%(amount,float(total_note[0][0]),cr_frm.document_type))

	if cr_frm.type == 'Sales Invoice' :

		frappe.db.sql(""" UPDATE `tabSales Invoice` SET outstanding_amount = %d,
						total_discount_note =%d WHERE name ='%s'"""%(amount,float(total_note[0][0]),cr_frm.document_type))

	frappe.db.commit()

	



def create_name():
	leng = 10
	letters = string.ascii_lowercase
	result = ''.join(random.choice(letters) for i in range(leng))
	return str(result)