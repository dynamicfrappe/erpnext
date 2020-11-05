// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Company Loans Report"] = {
	"filters": [
               {
			"fieldname":"name",
			"label": __("Bank Name"),
			"fieldtype": "Link",
			"options":"Bank"

		},
		{
			"fieldname":"due_date",
			"label": __("From Date"),
			"fieldtype": "Date"
			

		},
		{
			"fieldname":"to_due_date",
			"label": __("To Date"),
			"fieldtype": "Date"
			

		},
	]
};
