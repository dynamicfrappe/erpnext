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
			"label": _("Iem Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options":"Item",
			"width": 150
		},
			{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 150
		},
			{
			"label": _("Quantity"),
			"fieldname": "qty",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("purchase order"),
			"fieldname": "poname",
			"fieldtype": "Link",
			"options":"Purchase Order",
			"width": 150
		},

		{
			"label": _("Purchase Invoice"),
			"fieldname": "purchaseinvoice",
			"fieldtype": "Link",
			"options":"Purchase Invoice",
			"width": 150
		},
			
		
		
	]
	

	return columns

def get_data(filters):
	condition=""
	results=[]
	res=[]
	if filters.get("Supplier"):
		condition +=" AND tabSupplier.`name` = '%s'"%filters.get("Supplier")
	if filters.get("fromDate"):
		condition += " AND `tabPurchase Order`.schedule_date >= '%s' "%filters.get("fromDate")
		condition +=" AND `tabPurchase Invoice`.due_date >= '%s' "%filters.get("fromDate")
	if filters.get("toDate"):
		condition += " AND `tabPurchase Order`.schedule_date <= '%s' "%filters.get("toDate")
		condition += "AND `tabPurchase Invoice`.due_date >= '%s'"%filters.get("toDate")
    

	if filters.get("Supplier"):


		results=frappe.db.sql("""  
					select `tabPurchase Invoice Item`.item_code,
					        `tabPurchase Invoice Item`.item_name,
					        `tabPurchase Invoice Item`.qty,
					        (select count(*) from`tabPurchase Order` where `tabPurchase Order`.supplier=tabSupplier.name) as 'poname',
					        (select count(*) from`tabPurchase Invoice` where `tabPurchase Invoice`.supplier=tabSupplier.name) as 'purchaseinvoice',
					        tabSupplier.name
					from `tabPurchase Order`
					inner join
					    tabSupplier
					on `tabPurchase Order`.supplier=tabSupplier.name
					inner join
					   `tabPurchase Invoice`
					on `tabPurchase Invoice`.supplier=tabSupplier.name

					inner join
					    `tabPurchase Invoice Item`
					on `tabPurchase Invoice Item`.parent=`tabPurchase Invoice`.name
	       		   where 1=1
	       		   {condition}
	    		 group by `tabPurchase Invoice Item`.item_code,`tabPurchase Order`.name, `tabPurchase Invoice`.name;
	             

		""".format(condition=condition) ,as_dict=1)
		for index in range(0,len(results)):
			
			for index2 in range(index+1,len(results)):
				if results[index]["poname"] == results[index2]["poname"]:
					results[index2]["poname"] =""
				if results[index]["purchaseinvoice"] == results[index2]["purchaseinvoice"]:
					results[index2]["purchaseinvoice"] =""
				if results[index]["item_code"] == results[index2]["item_code"]:
					results[index]["qty"] +=results[index2]["qty"]
				if results[index]["item_code"] == results[index2]["item_code"]:
					results[index2]["item_code"] =""
					results[index2]["item_name"] =""
					results[index2]["qty"] =""




	for c1 in range(0,len(results)):
		for c2 in range(c1+1,len(results)):
			if results[c1]["item_code"]=="":
				results[c1]["item_code"] =results[c2]["item_code"]
				results[c1]["item_name"] =results[c2]["item_name"]
				results[c1]["qty"] =results[c2]["qty"]
				results[c2]["item_code"]=""
				results[c2]["item_name"]=""
				results[c2]["qty"]=""
			if results[c1]["purchaseinvoice"]=="":
				results[c1]["purchaseinvoice"]=results[c2]["purchaseinvoice"]
				results[c2]["purchaseinvoice"]=""
			if results[c1]["poname"]=="":
				results[c1]["poname"]=results[c2]["poname"]
				results[c2]["poname"]=""
		
	for x in results:
		if x["poname"] != "" or x["purchaseinvoice"]!="" or x["item_code"]!="":	
			res.append(x)

		

	return res



