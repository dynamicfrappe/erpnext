// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Assts Movement Report"] = {
	"filters": [
		{
			"fieldname":"asset_name",
			"label": __("Asset Name"),
			"fieldtype": "Link",
			"options":"Asset"

		},
		{
			"fieldname":"employee_name",
			"label": __("Employee Name"),
			"fieldtype": "Link",
			"options":"Employee"

		},
		{
			"fieldname":"Department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options":"Department"

		},
		{
			"fieldname":"Project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options":"Project"

		},
	]
};
