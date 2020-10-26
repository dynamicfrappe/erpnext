# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data    = get_data(filters)
	return columns, data




# Get Grid Columns
def get_columns():
	return [
		{
			"label": _("Purchase Order"),
			"fieldname": "purchase_order",
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 200
		},
		{
			"label": _("Purchase Invoice"),
			"fieldname": "purchase_invoice",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 200
		},
		{
			"label": _("Item"),
			"fieldname": "item_name",
			"fieldtype": "data",
			"width": 200
		},
		{
			"label": _("PO Price"),
			"fieldname": "PO_Rate",
			"fieldtype": "Currency",
			"options" : "currency" ,
			"width": 200
		},
		{
			"label": _("PI Rate"),
			"fieldname": "PI_Rate",
			"fieldtype": "Currency",
			"options" : "currency" ,
			"width": 200
		}
	]

# get data
def get_data(filters):
	data = get_Invoices_with_purchase_order(filters)
	return data



# Main Method to Execute Query
def get_Invoices_with_purchase_order(filters):

	conditions = ""
	
	if filters.get("Invoice_No"):
		conditions += " and PI.parent =%(Invoice_No)s"

	if filters.get("Purchase_Order"):
		conditions += " and PO.parent =%(Purchase_Order)s"


	results = frappe.db.sql("""

	    	   select  PI.parent as purchase_invoice, PO.parent as purchase_order ,PI.item_name , PI.Rate as PI_Rate , PO.Rate as PO_Rate   from `tabPurchase Invoice Item`  PI 
			   inner JOIN `tabPurchase Order Item`  PO On PI.purchase_order = PO.parent And  PI.item_code = PO.item_code 
				where  ISNULL( PI.purchase_order ) = 0
		{conditions}
		
		""".format(conditions=conditions), filters, as_dict=1)
	return results
