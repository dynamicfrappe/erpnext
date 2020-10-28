# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime

class OnHold(Document):
	def validate(self):
		for item in self.get("ob_hold_items") :
			data = frappe.db.sql("""
				SELECT IFNULL(qty_after_transaction,0) as qty_after_transaction  from `tabStock Ledger Entry`  
				WHERE item_code = '{item_code}' AND warehouse = '{warehouse}'
				ORDER BY `name` DESC Limit 1
			""".format(item_code = item.item_code , warehouse = item.warehouse) , as_dict=1)
			total_hold_qty_in_warehouse = get_holding_qty_in_warehouse (item.item_code , item.warehouse , self.name)

			if not data[0].qty_after_transaction:
				data[0].qty_after_transaction = 0
			if item.qty > (data[0].qty_after_transaction - total_hold_qty_in_warehouse) :
					frappe.throw(_(" Item {item_code} don't have the required qty in stock {warehouse} " .format(item_code = item.item_code , warehouse = item.warehouse)));
					frappe.validated=false;
					return false
			





@frappe.whitelist()
def get_item_wharehouse(item,qtyy,name,*args,**kwargs):
	if not name :
				name = '#'
	items = []
	sql = frappe.db.sql("""
							SELECT   warehouse , qty_after_transaction
							from `tabStock Ledger Entry`  
							where `name` IN ( 
							SELECT MAX(`name`) from  `tabStock Ledger Entry` GROUP BY item_code , warehouse)
							
							and qty_after_transaction <>0 and item_code = '%s' AND  qty_after_transaction >= %d
							

							GROUP BY item_code , warehouse  """ %(str(item) ,int(qtyy)) , as_dict = 1)
	qty = float(qtyy)
	if sql:
		# case when  one multi warehouse has qty > required qty take first warehouse
		for record in sql :
				total_hold_qty = get_holding_qty_in_warehouse(item,record.warehouse , name)
				if (record.qty_after_transaction-total_hold_qty) >= qty :
						item_data = {
						'item_code' : str(item),
						'warehouse' : sql[0].warehouse,
						'qty' : float(qtyy)
						}
						items.append(item_data)
						break
		if len(items)==0:
			items=get_Multiple_qty_from_warehouses(item,qtyy,name)

	if not sql :
	    # try:
		# case when  multi warehouse has qty > required qty
		items=get_Multiple_qty_from_warehouses(item,qtyy,name)
			


	return items

def get_Multiple_qty_from_warehouses(item  , qty,name):
			items = []
			chech_all_available_stock = frappe.db.sql("""  			SELECT   Sum(qty_after_transaction) as total_qty 
																	from `tabStock Ledger Entry`  
																	where `name` IN ( 
																	SELECT MAX(`name`) from  `tabStock Ledger Entry` GROUP BY item_code , warehouse)
																	
																	and qty_after_transaction <>0 and item_code = '%s' 	

																	GROUP BY item_code  """%str(item) , as_dict = 1)
			if chech_all_available_stock :
				total_qty =  (chech_all_available_stock[0].total_qty) or 0
			else : total_qty = 0	
			total_hold_qty = get_holding_qty_in_all_warehouse (item,name)

			if not total_qty:
					total_qty = 0

			if (total_qty-total_hold_qty) >= float(qty):


					sql = frappe.db.sql(""" SELECT   warehouse  , qty_after_transaction as qty
											from `tabStock Ledger Entry`  
											where `name` IN ( 
											SELECT MAX(`name`) from  `tabStock Ledger Entry` GROUP BY item_code , warehouse)
											
											and qty_after_transaction <>0 and item_code = '%s' AND  qty_after_transaction > 0
											order by qty_after_transaction desc
											"""%(str(item)), as_dict = 1 )

					if len(sql) > 0:
						required_QTY = float(qty)

						for record in sql :
								total_hold_qty_in_warehouse = get_holding_qty_in_warehouse(item,record.warehouse,name)
								if (record.qty - total_hold_qty_in_warehouse) >= required_QTY:
									item_data = {
													'item_code' : str(item),
													'warehouse' : record.warehouse,
													'qty' : float(required_QTY)
												}
									items.append(item_data)
									required_QTY = 0
									break
								else :

									item_data = {
													'item_code' : str(item),
													'warehouse' : record.warehouse,
													'qty' : float(record.qty - total_hold_qty_in_warehouse)
												}
									items.append(item_data)
									required_QTY -= float((record.qty - total_hold_qty_in_warehouse))

						if required_QTY != 0 :
							items = []
			return items

def get_holding_qty_in_warehouse( item , warehouse , name = '#'):
				total_hold_qty = 0
				total_hold_qty_result = frappe.db.sql("""
												SELECT
												IFNULL(SUM(HRI.qty),0) as total_hold_qty
												FROM
												`tabOb Hold Items` HRI
												INNER JOIN
													`tabOn Hold` HR
												ON 
													HR.`name` = HRI.parent
													WHERE HR.`status` = 'Open' and HR.docstatus =1 and HRI.`parent` != '{name}'
													GROUP BY HRI.item_code , HRI.warehouse
													HAVING 	 HRI.item_code = '{item_code}' AND HRI.warehouse = '{warehouse}'

											     LIMIT 1
												""".format(item_code = item , warehouse = warehouse , name = name),as_dict=1)
				if not total_hold_qty_result:
					total_hold_qty = 0
				else :
					total_hold_qty = total_hold_qty_result[0].total_hold_qty
					if not total_hold_qty :
						total_hold_qty = 0
				return total_hold_qty

def get_holding_qty_in_all_warehouse( item , name = '#' ):


				total_hold_qty = 0
				total_hold_qty_result = frappe.db.sql("""
															SELECT
															IFNULL(SUM(HRI.qty),0) as total_hold_qty
															FROM
															`tabOb Hold Items` HRI
															INNER JOIN
																`tabOn Hold` HR
															ON 
																HR.`name` = HRI.parent
																WHERE HR.`status` = 'Open' and HR.docstatus =1 and HRI.`parent` != '{name}'
																GROUP BY HRI.item_code , HRI.warehouse
																HAVING 	 HRI.item_code = '{item_code}' 

														     LIMIT 1
															""".format(item_code = item ,name = name),as_dict=1)
				if not total_hold_qty_result:
					total_hold_qty = 0
				else :
					total_hold_qty = total_hold_qty_result[0].total_hold_qty
					if not total_hold_qty :
						total_hold_qty = 0
				return total_hold_qty

def close_On_hold ():
	frappe.db.sql("""	update `tabOn Hold`
						set `status` = 'Close'
						where `tabOn Hold`.end_date <= CURDATE()""")