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
			"fieldtype": "Data",
			"width": 150
		},
			{
			"label": _("Supplier Name"),
			"fieldname": "SupplierName",
			"fieldtype": "Link",
			"options":"Supplier",
			"width": 150
		},
		{
			"label": _("po"),
			"fieldname": "poname",
			"fieldtype": "Link",
			"options":"Purchase Order",
			"width": 150
		},
			{
			"label": _("Reqd By Date"),
			"fieldname": "schedule_date",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("po Total"),
			"fieldname": "pograndtotal",
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
			"label": _("Due Date"),
			"fieldname": "due_date",
			"fieldtype": "Data",
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
		condition +=" AND tabSupplier.`name` = '%s'"%filters.get("Supplier")
	if filters.get("fromDate"):
		condition += " AND `tabPurchase Order`.schedule_date >= '%s' "%filters.get("fromDate")
		condition +=" AND `tabPurchase Invoice`.due_date >= '%s' "%filters.get("fromDate")
	if filters.get("toDate"):
		condition += " AND `tabPurchase Order`.schedule_date <= '%s' "%filters.get("toDate")
		condition += "AND `tabPurchase Invoice`.due_date >= '%s'"%filters.get("toDate")


	print(condition)
	results=frappe.db.sql("""  
          select  tabSupplier.`name` as 'SupplierName',
       `tabPurchase Order`.name as 'poname',
       `tabPurchase Order`.schedule_date as 'schedule_date',
       `tabPurchase Order`.`grand_total` as 'pograndtotal',
       `tabPurchase Invoice`.`name` as 'purchaseinvoice',
       `tabPurchase Invoice`.due_date as 'due_date',
       `tabPurchase Invoice`.`grand_total` as 'total'
       FROM tabSupplier
         inner join
           `tabPurchase Order`
       on tabSupplier.name=`tabPurchase Order`.supplier_name
          inner join `tabPurchase Invoice`
         on `tabSupplier`.name =`tabPurchase Invoice`.supplier
       		   where 1=1
       		   {condition}
    		 group by tabSupplier.name,`tabPurchase Invoice`.name,`tabPurchase Order`.name
    		  order by tabSupplier.name
             


			
	""".format(condition=condition) ,as_dict=1)

	res=[]

	for index in range(0,len(results)):
		for index2 in range(index+1,len(results)):
			if results[index]["poname"] == results[index2]["poname"]:
				results[index2]["poname"] =""
			if results[index]["purchaseinvoice"] == results[index2]["purchaseinvoice"]:
				results[index2]["purchaseinvoice"] =""

	for x in results:
		if x["poname"] != "" or x["purchaseinvoice"]!="" :	
			res.append(x)
		




			
          


	return res



