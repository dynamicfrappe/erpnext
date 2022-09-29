# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import datetime
def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data    = get_data(filters)
	return columns, data




def get_columns(filters):
	columns = [
		{
			"label": _("Bank Name"),
			"fieldname": "liabilities",
			"fieldtype": "Link",
			"options":"Bank",
			"width": 150
		},
		    {
			"label": _("Due date"),
			"fieldname": "due_date",
			"fieldtype": "data",
			"width": 150
		},
		{
			"label": _("The number of payments made"),
			"fieldname": "the_number_of_payments_made",
			"width": 150
		},
		    {
			"label": _("Amount"),
			"fieldname": "in",
			"fieldtype": "data",
			"width": 150
		},
		{
			"label": _("Total amount"),
			"fieldname": "total",
			"width": 150
		},
		
		
	]
	

	return columns

def get_data(filters):
	condition=""
	if filters.get("name"):
		condition +="AND `tabCompany Loans`.liabilities = '%s'"%filters.get("name")
	if filters.get("due_date") :
		condition += " AND `tabCompany Loans`.due_date >= '%s'"%filters.get("due_date")
	if filters.get("to_due_date"):
			condition += "And  `tabCompany Loans`.due_date <='%s'"%filters.get("to_due_date")
	results=frappe.db.sql("""
	            select * from `tabCompany Loans`
				where 1=1
                  {condition}
				
		
	       """.format(condition=condition) ,as_dict=1)

	return results


