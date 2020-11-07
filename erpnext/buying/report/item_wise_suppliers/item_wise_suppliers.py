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
			"label": _("Supplier"),
			"fieldname": "supplier_code",
			"fieldtype": "Link",
			"options":"Supplier",
			"width": 150
		},
			{
			"label": _("Supplier Name"),
			"fieldname": "SupplierName",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Number of Po"),
			"fieldname": "count",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Purchase Invoice"),
			"fieldname": "purchaseinvoice",
			"fieldtype": "Link",
			"options":"Purchase Invoice",
			"width": 150
		},
		{
			"label": _("Total"),
			"fieldname": "total",
			"fieldtype": "Data",
			"width": 150
		},
			
		
		
	]
	

	return columns

def get_data(filters):
	condition=""
	if filters.get("Supplier"):
		condition +="AND tabSupplier.`name` = '%s'"%filters.get("Supplier")
	if filters.get("fromDate"):
		condition += " AND `tabPurchase Order`.schedule_date >= '%s' "%filters.get("fromDate")
	if filters.get("toDate"):
		condition += " AND `tabPurchase Order`.schedule_date <= '%s' "%filters.get("toDate")


	print(condition)
	results=frappe.db.sql("""  
			select  tabSupplier.`name` as 'SupplierName',
      		 `tabPurchase Order`.`supplier` as 'supplier_code',
      		(select count(`tabPurchase Order`.`name`)from `tabPurchase Order` where `tabPurchase Order`.supplier= tabSupplier.`name`) as 'count',
      		 `tabPurchase Invoice`.`name` as 'purchaseinvoice',
      		 sum(`tabPurchase Invoice`.`base_grand_total`) as 'total'
      		 FROM tabSupplier
       		  left join
       	    `tabPurchase Order`
     		  on tabSupplier.name=`tabPurchase Order`.supplier_name
      		   left join `tabPurchase Invoice`
       		  on `tabPurchase Order`.name=(select `tabPurchase Invoice Item`.purchase_order from `tabPurchase Invoice Item` where `tabPurchase Invoice Item`.parent=`tabPurchase Invoice`.name limit 1)
       		   where 1=1
       		   {condition}
    		 group by `tabPurchase Order`.name,tabSupplier.name
    		  order by tabSupplier.name
             


			
	""".format(condition=condition) ,as_dict=1)

	return results


