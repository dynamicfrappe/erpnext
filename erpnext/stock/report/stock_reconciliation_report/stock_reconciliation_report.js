// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Reconciliation Report"] = {
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
			fieldname: "rec_request",
			label: __("Stock Reconciliation"),
			fieldtype: "Link",
			options: "Stock Reconciliation",
			"get_query": function(){

				return {'filters': [['Stock Reconciliation', 'company','=', frappe.query_report.get_filter_value("Company") ]]}

			}
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date")
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date")
		}
		,
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
