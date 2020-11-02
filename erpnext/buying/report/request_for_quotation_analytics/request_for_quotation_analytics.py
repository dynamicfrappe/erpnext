# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	# chart = get_chart(filters)
	# message = "Here is a message"
	return columns, data
def get_columns(filters):
	columns = [
				{
				"label": _("Supplier Quotation"),
				"fieldname": "supplier_quotation",
				"fieldtype": "Link",
				"options": "Supplier Quotation",
				"width": 200
				},

				{"label": _("Supplier"),
				"fieldname": "supplier",
				"fieldtype": "Data",
				"width": 150

				},

				{"label": _("Grand Total"),
				"fieldname": "quotation_total",
				"fieldtype": "Data",
				"width": 100



				}]

	items = get_requested_items(filters)
	for item_name in items :
		print(len(item_name[0]))
		col_width=150
		if len(item_name[0]) > 15 :
			col_width = 200
		

		col = {
		"label":_(item_name) ,
		"fieldname" : str(item_name),
		"fieldtype" : "Data" ,
		"width": col_width

		} 

		columns.append(col)
	return columns
def get_data(filters):
	data = []
	suppliers_quotation = frappe.db.sql(""" SELECT DISTINCT parent FROM `tabSupplier Quotation Item`  WHERE request_for_quotation='%s' """%filters.get('r_f_q'))
	for i in suppliers_quotation :
		total = frappe.db.sql("""SELECT grand_total,supplier  FROM `tabSupplier Quotation` WHERE name='%s' """%i)
		prices = get_items_prices_from_qutations(i,filters)
		data_b =[]
		data_b.append(str(i[0]) )
		data_b.append(str(total[0][1]) )
		data_b.append(str(total[0][0]) ) 

		for rate in prices:
			data_b.append(rate)
		data.append(data_b)
	items = get_requested_items(filters)
	data_s = ["" , "Last Purchase Rate",""]
	for item_name in items :
		
		item_last_purchase_rate = get_item_last_purchase_price(item_name)
		try :
			data_s.append(str(item_last_purchase_rate[0]))
		except:
			data_s.append(str('0'))
		
	data.append(data_s)
	return (data)
@frappe.whitelist() 
def get_requested_items(filters):
	requested_items = frappe.db.sql("""SELECT item_name FROM `tabRequest for Quotation Item` WHERE parent ='%s' """%filters.get("r_f_q"))
	return requested_items 



def get_min_rate_for_item(item ,filters):
	item_price_rate = frappe.db.sql("""SELECT MIN(rate) FROM  `tabSupplier Quotation Item` WHERE request_for_quotation='%s' 
		 AND item_name='%s' """%(filters.get('r_f_q') , item))	
	try:
		return float(item_price_rate[0][0])
	except :
		return None


def get_items_prices_from_qutations(parent,filters):
	items = get_requested_items(filters)
	data = []
	for name in items:
		item_price_rate = frappe.db.sql("""SELECT rate FROM  `tabSupplier Quotation Item` WHERE request_for_quotation='%s' 
						 AND item_name='%s' AND parent='%s'"""%(filters.get('r_f_q') , name[0],parent[0]))

		

		try:
			if item_price_rate[0][0] > 0 :
				minn = get_min_rate_for_item(name[0] ,filters)
				print(minn)
				if (minn and float(item_price_rate[0][0]) == minn ):
					data.append('<b style="background-color:green;">'+str(item_price_rate[0][0])+'</b>')
				else :
					data.append(item_price_rate[0][0])
		except:
			data.append('<b style="background-color:red;">'+str(0)+'</b>')

	return data




def get_item_last_purchase_price(item):
	data = frappe.db.sql(""" SELECT last_purchase_rate FROM `tabItem` WHERE item_name ='%s' """ %item)
	return data[0]






def get_chart(filters):
	labels =  get_requested_items(filters)
	items = get_requested_items(filters)
	data_set = []
	for i in items :
		set_d = {"name" : i ,
					"values" : [10]}
		data_set.append(set_d)


	chart = {
	'data':{
	'labels' : labels ,
	'datasets' :data_set

	},
	



	'isNavigable': 1,
    'type': 'bar'

	}

	return chart