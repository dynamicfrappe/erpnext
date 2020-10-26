# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OnHold(Document):
	pass



@frappe.whitelist()
def get_item_wharehouse(item,qtyy,*args,**kwargs):
	sql = frappe.db.sql(""" SELECT DISTINCT warehouse FROM `tabStock Ledger Entry` 
		WHERE  item_code = '%s' AND  actual_qty > %d"""%(str(item) ,int(qtyy)))
	qty = float(qtyy)
	if sql :
		check = "one"
	if not sql :
	    try:

			chech_all_available_stock = frappe.db.sql("""SELECT SUM(actual_qty) FROM `tabStock Ledger Entry` WHERE item_code = '%s'"""%str(item))
			num = str(chech_all_available_stock[0][0])
			qty =  (chech_all_available_stock[0])
			sql = frappe.db.sql(""" SELECT DISTINCT warehouse FROM `tabStock Ledger Entry` 
								WHERE  item_code = '%s' AND  actual_qty > 0"""%(str(item)))
			if len(sql) > 1:
				check = "many"
				qty = []
				ac_ct = 0
				for i in sql :
					qty_l  = frappe.db.sql("""SELECT actual_qty FROM `tabStock Ledger Entry` WHERE item_code = '%s' and warehouse='%s'

									"""	%(str(item) , str(i[0])))
					ac_ct += float(qty_l[0][0])
					if ac_ct < float(qtyy) :
						qty.append(float(qty_l[0][0]))
					else :
						a = float(qtyy) - sum(qty)
						qty.append(a)

			else:
				check ='one'
				sql= ["home"]
			

		except :
			qty = 0
		

	return({"item_code":item ,"qty":qty , "data":sql ,"check":check})