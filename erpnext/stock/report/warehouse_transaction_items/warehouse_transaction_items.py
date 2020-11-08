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
			'fieldname': "warehouse",
			'label': _("Warehouse"),
			'fieldtype': "Link",
			'options':'Warehouse',
			"width": 200
		},
		
		{
			'fieldname': "item_code",
			'label': _("Item"),
			'fieldtype': "Link",
			'options':'Item',
			"width": 200
		},
		
		
		{
			'fieldname': "stock_uom",
			'label': _("UOM"),
			'fieldtype': "Data",
			"width": 200
		},
		{
			'fieldname': "total_in",
			'label': _("Total In Transaction"),
			'fieldtype': "Float",
			"width": 200
		},
		{
			'fieldname': "total_out",
			'label': _("Total Out Transaction"),
			'fieldtype': "Float",
			"width": 200,
			"text-align" : "left"
		}
		
	]
	return columns
def getdata (filters):
	conditions = ""
	if filters.get("Company"):
		conditions = " and entry.company  =%(Company)s"
		if filters.get("item_code"):
			conditions += " and entry.item_code =%(item_code)s"
		if filters.get("warehouse"):
			conditions += " and entry.warehouse  =%(warehouse)s"
		if filters.get("from_date"):
			conditions += " and entry.posting_date  >=%(from_date)s"
		if filters.get("to_date"):
			conditions += " and entry.posting_date  <=%(to_date)s"


		results = frappe.db.sql("""
					select  entry.warehouse as warehouse, item.name as item_code,item.item_name as item_name, item.stock_uom  as stock_uom ,
				    SUM(case when entry.actual_qty >= 0 then 1 else 0 end) as total_in ,
				    SUM(case when entry.actual_qty < 0 then 1 else 0 end) as total_out
				    from `tabStock Ledger Entry` entry
				    inner join tabItem item on item.name = entry.item_code
				where  entry.docstatus = 1 and entry.is_cancelled = 'No'
					{conditions}

				group by entry.item_code, entry.warehouse
				order by warehouse,item_code , entry.posting_date desc
			
			""".format(conditions=conditions), filters, as_dict=1)


		return results