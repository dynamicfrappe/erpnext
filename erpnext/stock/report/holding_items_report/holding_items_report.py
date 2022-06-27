# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = getColumns(filters)
	data = getdata(filters)
	return columns, data
def getColumns (filters):
	columns = [
		{
			'fieldname': "Hold_request",
			'label': _("On Hold"),
			'fieldtype': "Link",
			'options': "On Hold",
			"width": 170
		},
		{
			'fieldname': "sales_order",
			'label': _("Sales Order"),
			'fieldtype': "Link",
			'options': "Sales Order",
			"width": 150
		},
		{
			'fieldname': "Item_code",
			'label': _("Item"),
			'fieldtype': "Link",
			'options':'Item',
			"width": 200
		},
		{
			'fieldname': "warehouse",
			'label': _("Warehouse"),
			'fieldtype': "Link",
			'options':'Warehouse',
			"width": 200
		},
		{
			'fieldname': "qty",
			'label': _("Qty"),
			'fieldtype': "Float",
			"width": 50
		},
		{
			'fieldname': "delivered_qty",
			'label': _("Delivered Qty"),
			'fieldtype': "Float",
			"width": 100
		},
		{
			'fieldname': "pending_qty",
			'label': _("Pending Qty"),
			'fieldtype': "Float",
			"width": 100
		},
		{
			'fieldname': "status",
			'label': _("Status"),
			'fieldtype': "Data",
			"width": 100
		},
		{
			'fieldname': "start_date",
			'label': _("Start Date"),
			'fieldtype': "Date",
			"width": 100
		},
		{
			'fieldname': "end_date",
			'label': _("End Date"),
			'fieldtype': "Date",
			"width": 100
		}
		
	]
	return columns
def getdata (filters):
	conditions = ""
	docstatus = 1
	if filters.get("Company"):
		conditions = " where `tabOn Hold`.`company` =%(Company)s "
	
		if filters.get("hold_request"):
			conditions += " and `tabOn Hold`.`name` =%(hold_request)s"	
		if filters.get("sales_order"):
			conditions += " and `tabOn Hold`.sales_order =%(sales_order)s"	
		if filters.get("status"):
			conditions += " and `tabOn Hold`.`status` =%(status)s"
			case = filters.get("status")
			if case == "Canceled":
				docstatus = 2


		if filters.get("item_code"):
			conditions += " and `tabOb Hold Items`.item_code =%(item_code)s"
		if filters.get("warehouse"):
			conditions += " and `tabOb Hold Items`.warehouse  =%(warehouse)s"


		results = frappe.db.sql("""
					SELECT
					`tabOn Hold`.`name` as Hold_request, 
					`tabOb Hold Items`.item_code as Item_code, 
					`tabOb Hold Items`.qty as qty, 
					`tabOb Hold Items`.pending_qty as pending_qty, 
					`tabOb Hold Items`.delivered_qty as delivered_qty, 
					`tabOb Hold Items`.warehouse as warehouse, 
					`tabOn Hold`.sales_order, 
					`tabOn Hold`.end_date, 
					`tabOn Hold`.start_date, 
					`tabOn Hold`.`status`
				FROM
					`tabOn Hold`
					INNER JOIN
					`tabOb Hold Items`
					ON 
						`tabOn Hold`.`name` = `tabOb Hold Items`.parent
					{conditions}
					and `tabOn Hold`.docstatus = {docstatus}
			
			""".format(conditions=conditions , docstatus = docstatus), filters, as_dict=1)
		return results