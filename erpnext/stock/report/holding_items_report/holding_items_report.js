// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Holding Items Report"] = {
	"filters": [
		
		{
			fieldname: "Company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd :1,
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "hold_request",
			label: __("On Hold"),
			fieldtype: "Link",
			options: "On Hold",
			"get_query": function(){

				return {'filters': [['On Hold', 'company','=', frappe.query_report.get_filter_value("Company") ]]}

			}
		},
		{
			fieldname: "sales_order",
			label: __("Sales Order"),
			fieldtype: "Link",
			options: "Sales Order",
			"get_query": function(){

				return {'filters': [['Sales Order', 'company','=', frappe.query_report.get_filter_value("Company") ]]}

			}
		}
		,
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ['Open','Close','Canceled'],
			default: 'Open'
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: 'Item'
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: 'Warehouse'
		}


	]
};
