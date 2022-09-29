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
			'label': _("Item"),
			'fieldtype': "Link",
			'options':'Item',
			"width": 150
		},
		
		
		{
			'fieldname': "stagnant_duration_days",
			'label': _("Stagnant Days"),
			'fieldtype': "Data",
			"width": 200
		},
		{
			'fieldname': "last_transaction_type",
			'label': _("Last Transaction Type"),
			'fieldtype': "Data",
			"width": 150
		},
		{
			'fieldname': "last_transaction",
			'label': _("Last Transaction"),
			'fieldtype': "Dynamic Link",
			'options' : "last_transaction_type",
			"width": 200,
			"text-align" : "left"
		},
		{
			'fieldname': "posting_date",
			'label': _("Transaction Date"),
			'fieldtype': "Date",
			"width": 150
		},
		
		{
			'fieldname': "due_date",
			'label': _("Stagnant Date"),
			'fieldtype': "Date",
			"width": 150
		},
		
		
		{
			'fieldname': "days",
			'label': _("Stagnant Days"),
			'fieldtype': "Data",
			"width": 150
		},
		{
			'fieldname': "last_purchase_date",
			'label': _("Last Purchase Date"),
			'fieldtype': "Date",
			"width": 150
		},
		{
			'fieldname': "receipt_name",
			'label': _("Purchase Receipt"),
			'fieldtype': "Link",
			'options': 'Purchase Receipt',
			"width": 150,
			"text-align" : "left"
		}
		,
		{
			'fieldname': "opening_entry_date",
			'label': _("Last Opening Date"),
			'fieldtype': "Date",
			"width": 100
		},
		{
			'fieldname': "opening_entry_name",
			'label': _("Last Opening Entry"),
			'fieldtype': "Link",
			'options': 'Stock Reconciliation',
			"width": 150,
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

		results = frappe.db.sql("""
					
					select item.name as item_code, item.item_name , item.stagnant_duration_days,  entry.voucher_no  as last_transaction ,entry.voucher_type  as last_transaction_type , entry.posting_date , (entry.posting_date  + ifnull(item.stagnant_duration_days,0)) as due_date , DATEDIFF(curdate() , entry.posting_date) as days
					, (select   posting_date as last_receipt_date from `tabStock Ledger Entry` ttt
					    where ttt.name in (
					    select MAX(name) from `tabStock Ledger Entry` where item_code = item.name  and voucher_type = 'Purchase Receipt'
					    group by item_code
					    )
					    ) as last_purchase_date
					, (select   ttt.voucher_no as last_receipt_date from `tabStock Ledger Entry` ttt
					    where ttt.name in (
					    select MAX(name) from `tabStock Ledger Entry` where item_code = item.name and voucher_type = 'Purchase Receipt'
					    group by item_code
					    )
					    ) as receipt_name
					, (select   ttt.voucher_no as last_opining_date from `tabStock Ledger Entry` ttt
					    where ttt.name in (
					    select MAX(name) from `tabStock Ledger Entry` where item_code = item.name and voucher_type in ('Stock Reconciliation')
					    group by item_code
					    )
					    ) as opening_entry_name
					, (select   ttt.posting_date as last_opining_date from `tabStock Ledger Entry` ttt
					    where ttt.name in (
					    select MAX(name) from `tabStock Ledger Entry` where item_code = item.name and voucher_type in ('Stock Reconciliation')
					    group by item_code
					    )
					    ) as opening_entry_date


					from `tabStock Ledger Entry` entry
					inner join tabItem item on item.name = entry.item_code
					where entry.name in (
					    select max(t.name) from `tabStock Ledger Entry` t  where t.docstatus = 1 and t.voucher_type in ('Delivery Note','Sales Invoice') and ifnull(t.actual_qty,0) < 0  group by  t.item_code , t.warehouse
					    ) and ifnull(item.stagnant_duration_days,0) != 0  and (entry.posting_date  + ifnull(item.stagnant_duration_days,0))< CURDATE()

					and ifnull(
					    (select count(tt.name) from `tabStock Ledger Entry` tt  where tt.docstatus = 1 and tt.item_code = item.name
					    )
					    ,0) != 0 
					{conditions}

				;
			
			""".format(conditions=conditions), filters, as_dict=1)


		return results