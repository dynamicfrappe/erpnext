// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Value Added Tax"] = {
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
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date"

		},
		{
			fieldname: "to_date",
			label: __("to Date"),
			fieldtype: "Date"

		}

	]
};
