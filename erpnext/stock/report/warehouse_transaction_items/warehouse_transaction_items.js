// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Warehouse Transaction items"] = {
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
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: 'Warehouse'
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: 'Item'
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date"
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date"
		}
	]
};
