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
			'fieldname': "item_code",
			'label': _("Item Code"),
			'fieldtype': "Link",
			'options': "Item",
			"width": 200
		},
		{
			'fieldname': "item_name",
			'label': _("Item Name"),
			'fieldtype': "Data",
			"width": 200
		},
		{
			'fieldname': "total_qty",
			'label': _("Total Qty in All Warehouses"),
			'fieldtype': "float",
			"width": 200
		},
		{
			'fieldname': "total_level_qty",
			'label': _("Total Level Qty"),
			'fieldtype': "float",
			"width": 200
		},
		{
			'fieldname': "total_required_qty",
			'label': _("Total Required Qty"),
			'fieldtype': "float",
			"width": 200
		}
		
	]
	return columns
def getdata (filters):
		conditions = ""

	
		if filters.get("item"):
			conditions += " and result.item_code = %(item)s"	

		results = frappe.db.sql("""
					select * , ifnull(result.total_qty1,0) as total_qty from (select
			       item.item_code , item.item_name ,
			       (SELECT SUM(IFNULL(qty_after_transaction,0)) as total_qty  from `tabStock Ledger Entry`
							WHERE item_code = item.name
							ORDER BY `name` DESC Limit 1) as total_qty1
			        ,sum(reorder.warehouse_reorder_level) as total_level_qty ,
			       sum(reorder.warehouse_reorder_qty) as total_required_qty

			from `tabItem Reorder` reorder inner join tabItem item on item.name = reorder.parent
			group by  item.name) result
			 where ifnull(result.total_qty1 ,0) < result.total_level_qty
					{conditions}
			
			""".format(conditions=conditions), filters, as_dict=1)
		return results