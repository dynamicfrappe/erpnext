# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data    = get_data(filters)
	return columns, data




def get_columns(filters):
	columns = [
		{
			"label": _("tabPurchase Order"),
			"fieldname": "PurchaseOrderName",
			"fieldtype": "Link",
			"options":"Purchase Order",
			"width": 150
		},
		    {
			"label": _("purchase Order Total"),
			"fieldname": "PurchaseOrderToal",
			"fieldtype": "data",
			"width": 150
		},
		{
			"label": _("Name"),
			"fieldname": "name",
			"width": 150
		},
		    {
			"label": _("Type"),
			"fieldname": "type",
			"fieldtype": "data",
			"width": 150
		},
		{
			"label": _("Total"),
			"fieldname": "total",
			"width": 150
		},
		
		
	]
	

	return columns

def get_data(filters):
	condition=""
	if filters.get("PurchaseOrder"):
		condition +="AND `tabPurchase Order`.name = '%s'"%filters.get("PurchaseOrder")
	if filters.get("Date"):
		condition += " AND `tabPurchase Order`.creation = '%s' "%filters.get("Date")
	
	results=frappe.db.sql("""
	            select `tabPurchase Order`.name as 'PurchaseOrderName',
	            `tabPurchase Order`.grand_total as 'PurchaseOrderToal',
	            `tabPurchase Invoice`.name as 'name',
	            'Purchase Invoice ' as 'type',
	            `tabPurchase Invoice`.grand_total as 'total'
                from
                   `tabPurchase Order`
                inner join
                `tabPurchase Invoice`
                on `tabPurchase Order`.name=(select `tabPurchase Invoice Item`.purchase_order from `tabPurchase Invoice Item` where parent=`tabPurchase Invoice`.name limit 1)
				where 1=1
                  {condition}
				
		
	       """.format(condition=condition) ,as_dict=1)
	results2=frappe.db.sql("""
	            
                select `tabPurchase Order`.name as 'PurchaseOrderName',
               `tabPurchase Order`.grand_total as 'PurchaseOrderToal',
               `tabPurchase Receipt`.name as 'name',
               'Purchase Receipt  ' as 'type',
               `tabPurchase Receipt`.grand_total as 'total'
                from
                   `tabPurchase Order`
                inner join
                `tabPurchase Receipt`
                 on `tabPurchase Order`.name=(select `tabPurchase Receipt Item`.purchase_order from `tabPurchase Receipt Item` where parent=`tabPurchase Receipt`.name limit 1)
				where 1=1

                  {condition}
				
		
	       """.format(condition=condition) ,as_dict=1)
	total=results+results2

	return total


