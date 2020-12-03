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
			'label': _("Sales Invoice"),
			'fieldtype': "Link",
			'options': "Sales Invoice",
			"width": 170
		},
		{
			'fieldname': "due_date",
			'label': _("Due Date"),
			'fieldtype': "Date",
			"width": 150
		},
		{
			'fieldname': "customer_name",
			'label': _("Customer"),
			'fieldtype': "Data",
			"width": 200
		},
		{
			'fieldname': "total",
			'label': _("Total"),
			'fieldtype': "float",
			"width": 75
		},
		{
			'fieldname': "net_total",
			'label': _("Net Total"),
			'fieldtype': "float",
			"width": 75
		},
		{
			'fieldname': "tax_rate",
			'label': _("Tax Rate"),
			'fieldtype': "float",
			"width": 75
		},
		{
			'fieldname': "tax_amount",
			'label': _("Tax Amount"),
			'fieldtype': "float",
			"width": 150
		},
		{
			'fieldname': "discount_amount",
			'label': _("Invoice Discount"),
			'fieldtype': "float",
			"width": 150
		}
	]
	return columns
def getdata (filters):
	conditions = ""
	if filters.get("Company"):
		conditions = " where invoice.`company` =%(Company)s"
	
		if filters.get("charge_type"):
			conditions += " and taxes.charge_type =%(charge_type)s"	
		if filters.get("from_date"):
			conditions += " and invoice.due_date >=%(from_date)s"	
		if filters.get("to_date"):
			conditions += " and invoice.due_date <=%(to_date)s"


		results = frappe.db.sql("""
					SELECT
							invoice.`name` ,
							invoice.due_date,
							invoice.customer_name ,
							customer.tax_id , 
							invoice.total,
							invoice.net_total,
							taxes.charge_type ,
							SUM(taxes.rate) as tax_rate , 
							SUM(taxes.tax_amount) as tax_amount,	
							invoice.discount_amount
							
						FROM
							`tabSales Invoice` invoice
							INNER JOIN
							`tabSales Taxes and Charges` taxes
							ON 
								invoice.`name` = taxes.parent
							INNER JOIN 
							  tabCustomer  customer
							ON 
							  invoice.customer = customer.`name`
							{conditions}
								
							GROUP BY 
							invoice.`name` , taxes.charge_type
	
			
			""".format(conditions=conditions), filters, as_dict=1)
		return results