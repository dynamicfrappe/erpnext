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
			'fieldname': "quotation",
			'label': _("Quotation"),
			'fieldtype': "Link",
			'options': "Quotation",
			"width": 150
		},
		{
			'fieldname': "Q_total_qty",
			'label': _("Quotation Total Quantity"),
			'fieldtype': "float",
			"width": 200
		},
		{
			'fieldname': "Sales_order",
			'label': _("Sales Order"),
			'fieldtype': "Link",
			'options': "Sales Order",
			"width": 150
		},
		{
			'fieldname': "SO_cutomer",
			'label': _("Customer"),
			'fieldtype': "Link",
			'options': "Customer",
			"width": 200
		},
		{
			'fieldname': "SO_date",
			'label': _("SO Date"),
			'fieldtype': "Date",
			"width": 100
		},
		{
			'fieldname': "SO_total_qty",
			'label': _("SO Total Qty"),
			'fieldtype': "float",
			"width": 100
		},
		{
			'fieldname': "SO_total",
			'label': _("SO Total"),
			'fieldtype': "float",
			"width": 100
		}
		
	]
	return columns
def getdata (filters):
	conditions = ""
	if filters.get("Company"):
		conditions = " where QUO.`company` =%(Company)s"
	
		if filters.get("Quotation"):
			conditions += " and SOI.prevdoc_docname =%(Quotation)s"
		results = frappe.db.sql("""
					SELECT 
							QUO.`name` as quotation,
							QUO.total_qty as Q_total_qty, 
							SOI.parent as 'Sales_order',
							SO.customer as SO_cutomer,
							SO.transaction_date as SO_date,
							SO.total_qty as SO_total_qty, 
							SO.total as SO_total
							
				FROM `tabSales Order Item` SOI
				INNER JOIN `tabQuotation`QUO
				ON 
				QUO.`name` = SOI.prevdoc_docname
				INNER JOIN `tabSales Order` SO
				on SO.`name` = SOI.parent
					{conditions}
			
			""".format(conditions=conditions), filters, as_dict=1)
		return results