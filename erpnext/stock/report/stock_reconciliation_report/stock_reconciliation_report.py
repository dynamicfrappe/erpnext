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
			'fieldname': "name",
			'label': _("Stock Reconciliation"),
			'fieldtype': "Link",
			'options': "Stock Reconciliation",
			"width": 170
		},
		{
			'fieldname': "posting_date",
			'label': _("Posting Date"),
			'fieldtype': "Date",
			"width": 100
		},
		{
			'fieldname': "cost_center",
			'label': _("Cost Center"),
			'fieldtype': "Link",
			'options' : "Cost Center",
			"width": 100
		},
		{
			'fieldname': "item_code",
			'label': _("Item"),
			'fieldtype': "Link",
			'options':'Item',
			"width": 150
		},
		{
			'fieldname': "warehouse",
			'label': _("Warehouse"),
			'fieldtype': "Link",
			'options':'Warehouse',
			"width": 100
		},
		{
			'fieldname': "new_qty",
			'label': _("New Qty"),
			'fieldtype': "Data",
			"width": 75
		},
		{
			'fieldname': "old_qty",
			'label': _("Old Qty"),
			'fieldtype': "Data",
			"width": 75
		},
		{
			'fieldname': "quantity_difference",
			'label': _("Qty Difference"),
			'fieldtype': "Data",
			"width": 120
		},
		
		{
			'fieldname': "new_amount",
			'label': _("New Amount"),
			'fieldtype': "Data",
			"width": 100
		},
		{
			'fieldname': "old_amount",
			'label': _("Old Amount"),
			'fieldtype': "Currency",
			"width": 100
		},
		{
			'fieldname': "amount_difference",
			'label': _("Amount Difference"),
			'fieldtype': "Currency",
			"width": 120
		},
		{
			'fieldname': "old_valuation",
			'label': _("Old Valuation"),
			'fieldtype': "Currency",
			"width": 100
		},
		{
			'fieldname': "new_valuation",
			'label': _("New Valuation"),
			'fieldtype': "Currency",
			"width": 120
		}
		
	]
	return columns
def getdata (filters):
	conditions = ""
	docstatus = 1
	if filters.get("Company"):
		conditions = " and rec.`company` =%(Company)s "
	
		if filters.get("item_code"):
			conditions += " and item.item_code =%(item_code)s"
		if filters.get("warehouse"):
			conditions += " and item.warehouse =%(warehouse)s"
		if filters.get("from_date"):
			conditions += " and rec.posting_date >=%(from_date)s"
		if filters.get("to_date"):
			conditions += " and rec.posting_date <=%(to_date)s"

		results = frappe.db.sql("""
					select
						rec.name , item .warehouse , rec.posting_date , rec.cost_center , item.item_code , SUM(item.qty)  as new_qty, SUM(item.current_qty) as old_qty ,  SUM(item.quantity_difference) as quantity_difference,
						       SUM(item.amount)  as new_amount, SUM(item.current_amount) as old_amount ,  SUM(item.amount_difference) as amount_difference,
						       SUM(item.current_valuation_rate) as old_valuation , SUM(item.valuation_rate) as new_valuation
						from `tabStock Reconciliation Item` item inner join `tabStock Reconciliation` rec on item.parent = rec.name
						where rec.docstatus = 1
						{conditions}
						group by rec.name , item.item_code ,item .warehouse
			
			""".format(conditions=conditions , docstatus = docstatus), filters, as_dict=1)
		return results