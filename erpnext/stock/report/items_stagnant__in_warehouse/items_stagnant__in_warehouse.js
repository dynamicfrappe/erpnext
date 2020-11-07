// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Items Stagnant  in Warehouse"] = {
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
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: 'Item'
		}
	]
};
