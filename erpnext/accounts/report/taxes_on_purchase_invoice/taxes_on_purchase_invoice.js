// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Taxes on Purchase Invoice"] = {
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
			fieldname: "charge_type",
			label: __("Charge Type"),
			fieldtype: "Select",
   			options: "\nActual\nOn Net Total\nOn Previous Row Amount\nOn Previous Row Total\nOn Item Quantity",
   			reqd :1
			
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
