# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

suppliers = []
case_when = ""


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data    = get_data(filters)
	return columns, data





# Get Grid Columns
def get_columns(filters):
	columns = [
		{
			"label": _("RFQ"),
			"fieldname": "parent",
			"fieldtype": "Link",
			"options": "Request for Quotation",
			"width": 150
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("min Supplier Name "),
			"fieldname": "min_supplier",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Min Rate"),
			"fieldname": "min_rate",
			"fieldtype": "Data",
			"width": 150
		},
		
		{
			"label": _("Min Supplier Quotation"  ),
			"fieldname": "min_supplier_Q" ,
			"fieldtype": "Link",
			"options": "Supplier Quotation",
			"width": 150
		},
	
		{
			"label": _("Max Supplier Name "),
			"fieldname": "max_supplier",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Max Rate"),
			"fieldname": "max_rate",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Max Supplier Quotation"  ),
			"fieldname": "max_supplier_Q" ,
			"fieldtype": "Link",
			"options": "Supplier Quotation",
			"width": 150
		}
		
		
		
		
	]

	conditions = " where 1 =2 "
	if filters.get("RFQ_No"):
		conditions = " where  `tabRequest for Quotation Item`.parent =%(RFQ_No)s"

	results = frappe.db.sql("""

	 SELECT DISTINCT
	`tabSupplier Quotation`.supplier_name, 
	`tabSupplier Quotation`.supplier
	
	FROM
	`tabRequest for Quotation Item`
	INNER JOIN
	`tabSupplier Quotation Item`
	ON 
		`tabRequest for Quotation Item`.parent = `tabSupplier Quotation Item`.request_for_quotation AND
		`tabRequest for Quotation Item`.`name` = `tabSupplier Quotation Item`.request_for_quotation_item
	INNER JOIN
	`tabSupplier Quotation`
	ON 
		`tabSupplier Quotation Item`.parent = `tabSupplier Quotation`.`name`
		
			{conditions}


		
	""".format(conditions=conditions), filters, as_dict=1)

	global suppliers
	global case_when
	suppliers = []
	case_when = ""

	for row in results:

			case_when += ", SUM(case  `tabSupplier Quotation`.supplier when '"+row.supplier_name+"' then  `tabSupplier Quotation Item`.rate else 0 End) As 'rate_"+row.supplier_name+"'" 
			
			temp = [
				
				
				
				
				{
					"label": _("Rate Per Unit " + row.supplier_name ),
					"fieldname": "rate_" + row.supplier_name,
					"fieldtype": "Currency",
					"options" : "currency" ,
					"width": 150
				}
			]

			columns.extend(temp)
			suppliers.append(row)


	return columns

# get data
def get_data(filters):
	data = get_Invoices_with_purchase_order(filters)
	return data



# Main Method to Execute Query
def get_Invoices_with_purchase_order(filters):
	
	global suppliers
	global case_when

	conditions = "HAVING 1 = 2"

	
	if filters.get("RFQ_No"):
		conditions = " HAVING  tab.parent =%(RFQ_No)s"


	results = frappe.db.sql("""

	 SELECT
	 tab.parent,
	 tab.item_code, 
	 tab.item_name, 
	 tab.uom ,
	MIN(`tabSupplier Quotation Item`.rate) AS 'min_rate',
	MAX(`tabSupplier Quotation Item`.rate) AS 'max_rate',
(select SQ.supplier from `tabSupplier Quotation Item` SQI 
		INNER JOIN `tabSupplier Quotation` SQ on SQI.parent = SQ.`name`  
		where SQI.request_for_quotation_item =  tab.`name` and SQI.Rate = 
		 (select MIN(TT.rate)  from `tabSupplier Quotation Item` TT  where TT.request_for_quotation_item =  tab.`name`  ) LIMIT 1 )
			as min_supplier 
,
(select SQ.`name` from `tabSupplier Quotation Item` SQI 
		INNER JOIN `tabSupplier Quotation` SQ on SQI.parent = SQ.`name`  
		where SQI.request_for_quotation_item =  tab.`name` and SQI.Rate = 
		 (select MIN(TT.rate)  from `tabSupplier Quotation Item` TT  where TT.request_for_quotation_item =  tab.`name`  ) LIMIT 1 )
			as min_supplier_Q 
,

(select SQ.supplier from `tabSupplier Quotation Item` SQI 
		INNER JOIN `tabSupplier Quotation` SQ on SQI.parent = SQ.`name`  
		where SQI.request_for_quotation_item =  tab.`name` and SQI.Rate = 
		 (select MAX(TT.rate)  from `tabSupplier Quotation Item` TT  where TT.request_for_quotation_item =  tab.`name`  )  LIMIT 1 )
			as max_supplier 
,
(select SQ.`name` from `tabSupplier Quotation Item` SQI 
		INNER JOIN `tabSupplier Quotation` SQ on SQI.parent = SQ.`name`  
		where SQI.request_for_quotation_item =  tab.`name` and SQI.Rate = 
		 (select MAX(TT.rate)  from `tabSupplier Quotation Item` TT  where TT.request_for_quotation_item =  tab.`name`  ) LIMIT 1 )
			as max_supplier_Q 


	{case_when}
	
	FROM
	`tabRequest for Quotation Item` tab
	INNER JOIN
	`tabSupplier Quotation Item`
	ON 
		 tab.parent = `tabSupplier Quotation Item`.request_for_quotation AND
		 tab.`name` = `tabSupplier Quotation Item`.request_for_quotation_item
	INNER JOIN
	`tabSupplier Quotation`
	ON 
		`tabSupplier Quotation Item`.parent = `tabSupplier Quotation`.`name`
	
	
	 
	Group By 	tab.parent,tab.item_code , tab.item_name , tab.uom 
		
	{conditions}


		
	""".format(conditions=conditions , case_when = case_when), filters, as_dict=1)



	return results

