// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rejected Items"] = {
		"filters": [
		{
			"fieldname":"Wo",
			"label": __("Work Order"),
			"fieldtype": "Link",
			"options":"Work Order"

		},
		{
			"fieldname":"fromdate",
			"label": __("From Date"),
			"fieldtype": "Date",


		},
		{

			"fieldname":"todate",
			"label": __("To Date"),
			"fieldtype": "Date",

		},

	]
};
